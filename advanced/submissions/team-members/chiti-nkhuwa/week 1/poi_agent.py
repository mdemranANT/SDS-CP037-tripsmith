"""
POI (Points of Interest) Agent for TripSmith Multi-Agent Travel Planner
Gathers activities and points of interest based on user interests using search APIs and LLM processing
"""

import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio

from tavily import TavilyClient
from serpapi import GoogleSearch
from loguru import logger

from base_agent import BaseAgent
from schemas import (
    SearchRequest, AgentResponse, PointOfInterest, ActivityType, Currency
)


class POIAgent(BaseAgent):
    """Specialized agent for points of interest and activities search"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the POI Agent"""
        super().__init__("POIAgent", api_key)
        
        # Initialize search APIs
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        
        self.log_activity("POI Agent initialized successfully")
    
    async def process_request(self, request: SearchRequest) -> AgentResponse:
        """
        Process POI search request
        
        Args:
            request: Search request with destination and preferences
            
        Returns:
            AgentResponse with POI options
        """
        try:
            # Validate request
            if not self.validate_request(request):
                return self.create_response(
                    success=False,
                    error_message="Invalid search request"
                )
            
            self.log_activity(f"Processing POI search for {request.destination}")
            
            # Extract interests from preferences
            interests = self.extract_interests(request.preferences)
            
            # Search for POIs
            pois = await self.search_pois(request, interests)
            
            if not pois:
                return self.create_response(
                    success=False,
                    error_message="No points of interest found for the specified criteria",
                    reasoning="POI search returned no results"
                )
            
            # Categorize and filter POIs
            categorized_pois = await self.categorize_pois(pois, interests)
            
            # Normalize and rank POIs
            normalized_pois = await self.normalize_pois(categorized_pois, request)
            
            reasoning = f"Found {len(normalized_pois)} points of interest for {request.destination} across {len(set(p.category for p in normalized_pois))} categories"
            
            return self.create_response(
                success=True,
                data=normalized_pois,
                reasoning=reasoning
            )
            
        except Exception as e:
            self.log_activity(f"POI search failed: {str(e)}", "ERROR")
            return self.create_response(
                success=False,
                error_message=f"POI search error: {str(e)}"
            )
    
    def extract_interests(self, preferences: Dict[str, Any]) -> List[str]:
        """
        Extract user interests from preferences
        
        Args:
            preferences: User preferences dictionary
            
        Returns:
            List of interest categories
        """
        interests = preferences.get("interests", [])
        
        # Default interests if none specified
        if not interests:
            interests = ["cultural", "outdoor", "food", "entertainment"]
        
        # Map common interest terms to ActivityType categories
        interest_mapping = {
            "culture": "cultural",
            "history": "historical",
            "museum": "cultural",
            "art": "cultural",
            "nature": "nature",
            "outdoor": "outdoor",
            "hiking": "outdoor",
            "beach": "outdoor",
            "food": "food",
            "restaurant": "food",
            "shopping": "shopping",
            "entertainment": "entertainment",
            "nightlife": "entertainment",
            "sports": "outdoor"
        }
        
        mapped_interests = []
        for interest in interests:
            mapped_interest = interest_mapping.get(interest.lower(), interest.lower())
            if mapped_interest in [e.value for e in ActivityType]:
                mapped_interests.append(mapped_interest)
        
        return mapped_interests if mapped_interests else ["cultural", "outdoor"]
    
    async def search_pois(self, request: SearchRequest, interests: List[str]) -> List[Dict[str, Any]]:
        """
        Search for POIs using multiple APIs
        
        Args:
            request: Search request
            interests: List of interest categories
            
        Returns:
            List of POI data dictionaries
        """
        pois = []
        
        # Search for each interest category
        for interest in interests:
            try:
                # Search using Tavily
                tavily_results = await self.search_tavily(request, interest)
                pois.extend(tavily_results)
            except Exception as e:
                self.log_activity(f"Tavily search failed for {interest}: {str(e)}", "WARNING")
            
            try:
                # Search using SerpAPI
                serpapi_results = await self.search_serpapi(request, interest)
                pois.extend(serpapi_results)
            except Exception as e:
                self.log_activity(f"SerpAPI search failed for {interest}: {str(e)}", "WARNING")
        
        # Fallback: Generate mock POIs using LLM
        if not pois:
            self.log_activity("No API results, generating mock POIs")
            pois = await self.generate_mock_pois(request, interests)
        
        return pois
    
    async def search_tavily(self, request: SearchRequest, interest: str) -> List[Dict[str, Any]]:
        """Search POIs using Tavily API"""
        try:
            search_query = f"{interest} attractions and activities in {request.destination}"
            
            response = self.tavily_client.search(
                query=search_query,
                search_depth="basic",
                max_results=8
            )
            
            # Extract POI information from search results
            pois = []
            for result in response.get("results", []):
                poi_data = self.extract_poi_from_tavily(result, interest)
                if poi_data:
                    pois.append(poi_data)
            
            self.log_activity(f"Tavily found {len(pois)} {interest} POIs")
            return pois
            
        except Exception as e:
            self.log_activity(f"Tavily search error: {str(e)}", "ERROR")
            return []
    
    async def search_serpapi(self, request: SearchRequest, interest: str) -> List[Dict[str, Any]]:
        """Search POIs using SerpAPI"""
        try:
            if not self.serpapi_key:
                return []
            
            search = GoogleSearch({
                "q": f"{interest} attractions {request.destination}",
                "api_key": self.serpapi_key,
                "engine": "google"
            })
            
            results = search.get_dict()
            
            # Extract POI information from SerpAPI results
            pois = []
            organic_results = results.get("organic_results", [])
            
            for result in organic_results[:8]:  # Limit to 8 results
                poi_data = self.extract_poi_from_serpapi(result, interest)
                if poi_data:
                    pois.append(poi_data)
            
            self.log_activity(f"SerpAPI found {len(pois)} {interest} POIs")
            return pois
            
        except Exception as e:
            self.log_activity(f"SerpAPI search error: {str(e)}", "ERROR")
            return []
    
    def extract_poi_from_tavily(self, result: Dict[str, Any], interest: str) -> Optional[Dict[str, Any]]:
        """Extract POI data from Tavily search result"""
        try:
            content = result.get("content", "")
            title = result.get("title", "")
            
            # Use LLM to extract structured POI data
            prompt = f"""
            Extract point of interest information from this search result and return as JSON:
            
            Title: {title}
            Content: {content}
            Interest Category: {interest}
            
            Return JSON with these fields:
            - name: string
            - description: string
            - category: string (matching the interest category)
            - address: string
            - city: string
            - country: string
            - rating: float (0-5) if available
            - price_range: string ($, $$, $$$) if available
            - duration_hours: float (typical visit duration)
            - opening_hours: string if available
            - website: string if available
            - latitude: float if available
            - longitude: float if available
            
            If any field cannot be determined, use null.
            """
            
            # For now, return a mock POI based on the content
            return self.create_mock_poi_from_content(content, title, interest)
            
        except Exception as e:
            self.log_activity(f"Failed to extract POI from Tavily result: {str(e)}", "WARNING")
            return None
    
    def extract_poi_from_serpapi(self, result: Dict[str, Any], interest: str) -> Optional[Dict[str, Any]]:
        """Extract POI data from SerpAPI result"""
        try:
            # Extract structured data from SerpAPI response
            return {
                "name": result.get("title", "Unknown"),
                "description": result.get("snippet", "No description available"),
                "category": interest,
                "address": result.get("address", "Unknown"),
                "city": result.get("city", "Unknown"),
                "country": result.get("country", "Unknown"),
                "rating": result.get("rating", None),
                "price_range": result.get("price_range", None),
                "duration_hours": result.get("duration_hours", 2.0),
                "opening_hours": result.get("opening_hours", None),
                "website": result.get("link", None),
                "latitude": result.get("latitude", None),
                "longitude": result.get("longitude", None)
            }
            
        except Exception as e:
            self.log_activity(f"Failed to extract POI from SerpAPI result: {str(e)}", "WARNING")
            return None
    
    async def generate_mock_pois(self, request: SearchRequest, interests: List[str]) -> List[Dict[str, Any]]:
        """Generate mock POIs using LLM when APIs fail"""
        try:
            system_message = """You are a travel expert specializing in points of interest and activities. Generate realistic POI options based on the given criteria."""
            
            prompt = f"""
            Generate realistic points of interest for a trip to {request.destination} with interests in {', '.join(interests)}.
            
            Return the POIs as a JSON array with this structure:
            [
                {{
                    "name": "string",
                    "description": "string",
                    "category": "string (one of: cultural, outdoor, food, shopping, entertainment, historical, nature)",
                    "address": "string",
                    "city": "string",
                    "country": "string",
                    "rating": float (0-5),
                    "price_range": "string ($, $$, $$$)",
                    "duration_hours": float,
                    "opening_hours": "string",
                    "website": "string",
                    "latitude": float,
                    "longitude": float
                }}
            ]
            
            Generate 3-4 POIs for each interest category. Make them realistic with:
            - Varied ratings (2.5-5.0)
            - Different price ranges
            - Realistic visit durations (1-6 hours)
            - Mix of popular and hidden gems
            """
            
            response = await self.call_llm(prompt, system_message, temperature=0.7)
            json_data = self.extract_json_from_response(response)
            
            if json_data and isinstance(json_data, list):
                return json_data
            
            # Fallback to hardcoded mock POIs
            return self.get_hardcoded_mock_pois(request, interests)
            
        except Exception as e:
            self.log_activity(f"Mock POI generation failed: {str(e)}", "WARNING")
            return self.get_hardcoded_mock_pois(request, interests)
    
    def get_hardcoded_mock_pois(self, request: SearchRequest, interests: List[str]) -> List[Dict[str, Any]]:
        """Return hardcoded mock POIs as fallback"""
        mock_pois = []
        
        # Cultural POIs
        if "cultural" in interests:
            mock_pois.extend([
                {
                    "name": "City Museum of Art",
                    "description": "Renowned art museum featuring contemporary and classical collections",
                    "category": "cultural",
                    "address": "123 Art Street",
                    "city": request.destination,
                    "country": "United States",
                    "rating": 4.6,
                    "price_range": "$$",
                    "duration_hours": 3.0,
                    "opening_hours": "10:00 AM - 6:00 PM",
                    "website": "https://citymuseum.com",
                    "latitude": 34.0522,
                    "longitude": -118.2437
                },
                {
                    "name": "Historic Downtown Theater",
                    "description": "Beautifully restored theater hosting plays and performances",
                    "category": "cultural",
                    "address": "456 Theater Avenue",
                    "city": request.destination,
                    "country": "United States",
                    "rating": 4.3,
                    "price_range": "$$",
                    "duration_hours": 2.5,
                    "opening_hours": "Varies by show",
                    "website": "https://downtowntheater.com",
                    "latitude": 34.0522,
                    "longitude": -118.2437
                }
            ])
        
        # Outdoor POIs
        if "outdoor" in interests:
            mock_pois.extend([
                {
                    "name": "Central Park Gardens",
                    "description": "Beautiful botanical gardens with walking trails and seasonal flowers",
                    "category": "outdoor",
                    "address": "789 Garden Lane",
                    "city": request.destination,
                    "country": "United States",
                    "rating": 4.4,
                    "price_range": "$",
                    "duration_hours": 2.0,
                    "opening_hours": "8:00 AM - 8:00 PM",
                    "website": "https://centralparkgardens.com",
                    "latitude": 34.0522,
                    "longitude": -118.2437
                },
                {
                    "name": "Riverside Hiking Trail",
                    "description": "Scenic hiking trail along the river with mountain views",
                    "category": "outdoor",
                    "address": "321 Trail Road",
                    "city": request.destination,
                    "country": "United States",
                    "rating": 4.7,
                    "price_range": "Free",
                    "duration_hours": 4.0,
                    "opening_hours": "24/7",
                    "website": "https://riversidetrail.com",
                    "latitude": 34.0522,
                    "longitude": -118.2437
                }
            ])
        
        # Food POIs
        if "food" in interests:
            mock_pois.extend([
                {
                    "name": "Local Food Market",
                    "description": "Vibrant food market with local vendors and fresh produce",
                    "category": "food",
                    "address": "567 Market Street",
                    "city": request.destination,
                    "country": "United States",
                    "rating": 4.5,
                    "price_range": "$$",
                    "duration_hours": 1.5,
                    "opening_hours": "9:00 AM - 5:00 PM",
                    "website": "https://localfoodmarket.com",
                    "latitude": 34.0522,
                    "longitude": -118.2437
                },
                {
                    "name": "Famous Restaurant Row",
                    "description": "Street lined with diverse restaurants from around the world",
                    "category": "food",
                    "address": "890 Restaurant Boulevard",
                    "city": request.destination,
                    "country": "United States",
                    "rating": 4.2,
                    "price_range": "$$$",
                    "duration_hours": 2.0,
                    "opening_hours": "Varies by restaurant",
                    "website": "https://restaurantrow.com",
                    "latitude": 34.0522,
                    "longitude": -118.2437
                }
            ])
        
        # Entertainment POIs
        if "entertainment" in interests:
            mock_pois.extend([
                {
                    "name": "Downtown Entertainment District",
                    "description": "Vibrant area with bars, clubs, and live music venues",
                    "category": "entertainment",
                    "address": "234 Entertainment Way",
                    "city": request.destination,
                    "country": "United States",
                    "rating": 4.1,
                    "price_range": "$$",
                    "duration_hours": 3.0,
                    "opening_hours": "6:00 PM - 2:00 AM",
                    "website": "https://entertainmentdistrict.com",
                    "latitude": 34.0522,
                    "longitude": -118.2437
                }
            ])
        
        return mock_pois
    
    def create_mock_poi_from_content(self, content: str, title: str, interest: str) -> Dict[str, Any]:
        """Create a mock POI from search content"""
        return {
            "name": f"Mock {interest.title()} POI",
            "description": f"Mock {interest} attraction based on search results",
            "category": interest,
            "address": "123 Mock Street",
            "city": "Mock City",
            "country": "United States",
            "rating": 4.0,
            "price_range": "$$",
            "duration_hours": 2.0,
            "opening_hours": "10:00 AM - 6:00 PM",
            "website": "https://mockpoi.com",
            "latitude": 34.0522,
            "longitude": -118.2437
        }
    
    async def categorize_pois(self, pois: List[Dict[str, Any]], interests: List[str]) -> List[Dict[str, Any]]:
        """
        Categorize POIs based on interests and content analysis
        
        Args:
            pois: Raw POI data
            interests: User interest categories
            
        Returns:
            Categorized POI list
        """
        categorized_pois = []
        
        for poi in pois:
            # Ensure POI has a valid category
            category = poi.get("category", "cultural")
            if category not in [e.value for e in ActivityType]:
                # Try to categorize based on name and description
                category = self.categorize_poi_by_content(poi, interests)
            
            poi["category"] = category
            categorized_pois.append(poi)
        
        self.log_activity(f"Categorized {len(categorized_pois)} POIs")
        return categorized_pois
    
    def categorize_poi_by_content(self, poi: Dict[str, Any], interests: List[str]) -> str:
        """
        Categorize POI based on name and description content
        
        Args:
            poi: POI data
            interests: User interests
            
        Returns:
            Categorized activity type
        """
        name = poi.get("name", "").lower()
        description = poi.get("description", "").lower()
        
        # Simple keyword-based categorization
        if any(word in name + description for word in ["museum", "art", "gallery", "theater", "opera"]):
            return "cultural"
        elif any(word in name + description for word in ["park", "trail", "hiking", "beach", "outdoor"]):
            return "outdoor"
        elif any(word in name + description for word in ["restaurant", "cafe", "food", "market", "dining"]):
            return "food"
        elif any(word in name + description for word in ["mall", "shop", "store", "boutique"]):
            return "shopping"
        elif any(word in name + description for word in ["bar", "club", "nightlife", "entertainment"]):
            return "entertainment"
        elif any(word in name + description for word in ["historic", "monument", "castle", "ruins"]):
            return "historical"
        elif any(word in name + description for word in ["nature", "wildlife", "forest", "garden"]):
            return "nature"
        else:
            return interests[0] if interests else "cultural"
    
    async def normalize_pois(self, pois: List[Dict[str, Any]], request: SearchRequest) -> List[PointOfInterest]:
        """
        Normalize and validate POI data
        
        Args:
            pois: Raw POI data
            request: Original search request
            
        Returns:
            List of validated PointOfInterest objects
        """
        normalized_pois = []
        
        for poi_data in pois:
            try:
                # Convert to PointOfInterest object with validation
                poi = PointOfInterest(
                    name=poi_data.get("name", "Unknown"),
                    description=poi_data.get("description", "No description available"),
                    category=ActivityType(poi_data.get("category", "cultural")),
                    address=poi_data.get("address"),
                    city=poi_data.get("city", "Unknown"),
                    country=poi_data.get("country", "Unknown"),
                    rating=poi_data.get("rating"),
                    price_range=poi_data.get("price_range"),
                    duration_hours=poi_data.get("duration_hours"),
                    opening_hours=poi_data.get("opening_hours"),
                    website=poi_data.get("website"),
                    latitude=poi_data.get("latitude"),
                    longitude=poi_data.get("longitude")
                )
                
                normalized_pois.append(poi)
                
            except Exception as e:
                self.log_activity(f"Failed to normalize POI: {str(e)}", "WARNING")
                continue
        
        # Sort by rating and duration
        normalized_pois.sort(key=lambda x: (x.rating or 0, x.duration_hours or 0), reverse=True)
        
        self.log_activity(f"Normalized {len(normalized_pois)} POIs")
        return normalized_pois
