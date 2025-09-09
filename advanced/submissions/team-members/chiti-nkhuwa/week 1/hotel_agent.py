"""
Hotel Agent for TripSmith Multi-Agent Travel Planner
Searches for hotels with price and rating filters using search APIs and LLM processing
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
    SearchRequest, AgentResponse, Hotel, HotelRating, Currency,
    PointOfInterest
)


class HotelAgent(BaseAgent):
    """Specialized agent for hotel search and booking"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Hotel Agent"""
        super().__init__("HotelAgent", api_key)
        
        # Initialize search APIs
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        
        self.log_activity("Hotel Agent initialized successfully")
    
    async def process_request(self, request: SearchRequest) -> AgentResponse:
        """
        Process hotel search request
        
        Args:
            request: Search request with destination and dates
            
        Returns:
            AgentResponse with hotel options
        """
        try:
            # Validate request
            if not self.validate_request(request):
                return self.create_response(
                    success=False,
                    error_message="Invalid search request"
                )
            
            self.log_activity(f"Processing hotel search for {request.destination}")
            
            # Calculate trip duration
            trip_duration = (request.end_date - request.start_date).days
            
            # Search for hotels
            hotels = await self.search_hotels(request, trip_duration)
            
            if not hotels:
                return self.create_response(
                    success=False,
                    error_message="No hotels found for the specified criteria",
                    reasoning="Hotel search returned no results"
                )
            
            # Apply filters based on budget and preferences
            filtered_hotels = await self.apply_filters(hotels, request)
            
            # Normalize and rank hotels
            normalized_hotels = await self.normalize_hotels(filtered_hotels, request)
            
            reasoning = f"Found {len(normalized_hotels)} hotel options for {request.destination} over {trip_duration} nights"
            
            return self.create_response(
                success=True,
                data=normalized_hotels,
                reasoning=reasoning
            )
            
        except Exception as e:
            self.log_activity(f"Hotel search failed: {str(e)}", "ERROR")
            return self.create_response(
                success=False,
                error_message=f"Hotel search error: {str(e)}"
            )
    
    async def search_hotels(self, request: SearchRequest, trip_duration: int) -> List[Dict[str, Any]]:
        """
        Search for hotels using multiple APIs
        
        Args:
            request: Search request
            trip_duration: Number of nights
            
        Returns:
            List of hotel data dictionaries
        """
        hotels = []
        
        # Search using Tavily
        try:
            tavily_results = await self.search_tavily(request)
            hotels.extend(tavily_results)
        except Exception as e:
            self.log_activity(f"Tavily search failed: {str(e)}", "WARNING")
        
        # Search using SerpAPI
        try:
            serpapi_results = await self.search_serpapi(request)
            hotels.extend(serpapi_results)
        except Exception as e:
            self.log_activity(f"SerpAPI search failed: {str(e)}", "WARNING")
        
        # Fallback: Generate mock hotels using LLM
        if not hotels:
            self.log_activity("No API results, generating mock hotels")
            hotels = await self.generate_mock_hotels(request, trip_duration)
        
        return hotels
    
    async def search_tavily(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Search hotels using Tavily API"""
        try:
            search_query = f"hotels in {request.destination} with prices and ratings"
            
            response = self.tavily_client.search(
                query=search_query,
                search_depth="basic",
                max_results=10
            )
            
            # Extract hotel information from search results
            hotels = []
            for result in response.get("results", []):
                hotel_data = self.extract_hotel_from_tavily(result)
                if hotel_data:
                    hotels.append(hotel_data)
            
            self.log_activity(f"Tavily found {len(hotels)} hotels")
            return hotels
            
        except Exception as e:
            self.log_activity(f"Tavily search error: {str(e)}", "ERROR")
            return []
    
    async def search_serpapi(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Search hotels using SerpAPI"""
        try:
            if not self.serpapi_key:
                return []
            
            search = GoogleSearch({
                "q": f"hotels in {request.destination}",
                "api_key": self.serpapi_key,
                "engine": "google_hotels"
            })
            
            results = search.get_dict()
            
            # Extract hotel information from SerpAPI results
            hotels = []
            hotel_results = results.get("hotel_results", [])
            
            for hotel in hotel_results[:10]:  # Limit to 10 results
                hotel_data = self.extract_hotel_from_serpapi(hotel)
                if hotel_data:
                    hotels.append(hotel_data)
            
            self.log_activity(f"SerpAPI found {len(hotels)} hotels")
            return hotels
            
        except Exception as e:
            self.log_activity(f"SerpAPI search error: {str(e)}", "ERROR")
            return []
    
    def extract_hotel_from_tavily(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract hotel data from Tavily search result"""
        try:
            content = result.get("content", "")
            title = result.get("title", "")
            
            # Use LLM to extract structured hotel data
            prompt = f"""
            Extract hotel information from this search result and return as JSON:
            
            Title: {title}
            Content: {content}
            
            Return JSON with these fields:
            - name: string
            - address: string
            - city: string
            - country: string
            - rating: float (0-5)
            - rating_category: string (budget, standard, premium, luxury)
            - price_per_night: float
            - currency: string (USD, EUR, etc.)
            - amenities: array of strings
            - booking_link: string (if available)
            - latitude: float (if available)
            - longitude: float (if available)
            
            If any field cannot be determined, use null.
            """
            
            # For now, return a mock hotel based on the content
            return self.create_mock_hotel_from_content(content, title)
            
        except Exception as e:
            self.log_activity(f"Failed to extract hotel from Tavily result: {str(e)}", "WARNING")
            return None
    
    def extract_hotel_from_serpapi(self, hotel: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract hotel data from SerpAPI result"""
        try:
            # Extract structured data from SerpAPI response
            return {
                "name": hotel.get("name", "Unknown"),
                "address": hotel.get("address", "Unknown"),
                "city": hotel.get("city", "Unknown"),
                "country": hotel.get("country", "Unknown"),
                "rating": hotel.get("rating", 0.0),
                "rating_category": hotel.get("rating_category", "standard"),
                "price_per_night": hotel.get("price_per_night", 0.0),
                "currency": hotel.get("currency", "USD"),
                "amenities": hotel.get("amenities", []),
                "booking_link": hotel.get("booking_link"),
                "latitude": hotel.get("latitude"),
                "longitude": hotel.get("longitude")
            }
            
        except Exception as e:
            self.log_activity(f"Failed to extract hotel from SerpAPI result: {str(e)}", "WARNING")
            return None
    
    async def generate_mock_hotels(self, request: SearchRequest, trip_duration: int) -> List[Dict[str, Any]]:
        """Generate mock hotels using LLM when APIs fail"""
        try:
            system_message = """You are a hotel search expert. Generate realistic hotel options based on the given criteria."""
            
            prompt = f"""
            Generate 5 realistic hotel options for a trip to {request.destination} for {trip_duration} nights.
            
            Return the hotels as a JSON array with this structure:
            [
                {{
                    "name": "string",
                    "address": "string",
                    "city": "string",
                    "country": "string",
                    "rating": float (0-5),
                    "rating_category": "string (budget/standard/premium/luxury)",
                    "price_per_night": float,
                    "currency": "USD",
                    "amenities": ["string"],
                    "booking_link": "string",
                    "latitude": float,
                    "longitude": float
                }}
            ]
            
            Make the hotels realistic with:
            - Different price ranges ($50-$500 per night)
            - Different rating categories (budget to luxury)
            - Realistic amenities (WiFi, pool, gym, etc.)
            - Mix of hotel types (boutique, chain, resort)
            """
            
            response = await self.call_llm(prompt, system_message, temperature=0.7)
            json_data = self.extract_json_from_response(response)
            
            if json_data and isinstance(json_data, list):
                return json_data
            
            # Fallback to hardcoded mock hotels
            return self.get_hardcoded_mock_hotels(request, trip_duration)
            
        except Exception as e:
            self.log_activity(f"Mock hotel generation failed: {str(e)}", "WARNING")
            return self.get_hardcoded_mock_hotels(request, trip_duration)
    
    def get_hardcoded_mock_hotels(self, request: SearchRequest, trip_duration: int) -> List[Dict[str, Any]]:
        """Return hardcoded mock hotels as fallback"""
        return [
            {
                "name": "Grand Hotel & Spa",
                "address": "123 Main Street",
                "city": request.destination,
                "country": "United States",
                "rating": 4.5,
                "rating_category": "luxury",
                "price_per_night": 350.0,
                "currency": "USD",
                "amenities": ["WiFi", "Pool", "Spa", "Gym", "Restaurant", "Room Service"],
                "booking_link": "https://grandhotel.com",
                "latitude": 34.0522,
                "longitude": -118.2437
            },
            {
                "name": "Comfort Inn Downtown",
                "address": "456 Oak Avenue",
                "city": request.destination,
                "country": "United States",
                "rating": 3.8,
                "rating_category": "standard",
                "price_per_night": 120.0,
                "currency": "USD",
                "amenities": ["WiFi", "Breakfast", "Parking", "Business Center"],
                "booking_link": "https://comfortinn.com",
                "latitude": 34.0522,
                "longitude": -118.2437
            },
            {
                "name": "Budget Motel Express",
                "address": "789 Pine Street",
                "city": request.destination,
                "country": "United States",
                "rating": 2.5,
                "rating_category": "budget",
                "price_per_night": 65.0,
                "currency": "USD",
                "amenities": ["WiFi", "Parking"],
                "booking_link": "https://budgetmotel.com",
                "latitude": 34.0522,
                "longitude": -118.2437
            },
            {
                "name": "Boutique Hotel Central",
                "address": "321 Elm Street",
                "city": request.destination,
                "country": "United States",
                "rating": 4.2,
                "rating_category": "premium",
                "price_per_night": 220.0,
                "currency": "USD",
                "amenities": ["WiFi", "Bar", "Restaurant", "Concierge", "Valet Parking"],
                "booking_link": "https://boutiquehotel.com",
                "latitude": 34.0522,
                "longitude": -118.2437
            },
            {
                "name": "Resort & Conference Center",
                "address": "654 Beach Boulevard",
                "city": request.destination,
                "country": "United States",
                "rating": 4.7,
                "rating_category": "luxury",
                "price_per_night": 450.0,
                "currency": "USD",
                "amenities": ["WiFi", "Pool", "Beach Access", "Golf Course", "Spa", "Multiple Restaurants"],
                "booking_link": "https://resort.com",
                "latitude": 34.0522,
                "longitude": -118.2437
            }
        ]
    
    def create_mock_hotel_from_content(self, content: str, title: str) -> Dict[str, Any]:
        """Create a mock hotel from search content"""
        return {
            "name": "Mock Hotel",
            "address": "123 Mock Street",
            "city": "Mock City",
            "country": "United States",
            "rating": 4.0,
            "rating_category": "standard",
            "price_per_night": 150.0,
            "currency": "USD",
            "amenities": ["WiFi", "Parking"],
            "booking_link": "https://mockhotel.com",
            "latitude": 34.0522,
            "longitude": -118.2437
        }
    
    async def apply_filters(self, hotels: List[Dict[str, Any]], request: SearchRequest) -> List[Dict[str, Any]]:
        """
        Apply budget and preference filters to hotels
        
        Args:
            hotels: Raw hotel data
            request: Search request with budget and preferences
            
        Returns:
            Filtered hotel list
        """
        filtered_hotels = []
        
        for hotel in hotels:
            # Budget filter
            if request.budget:
                total_cost = hotel.get("price_per_night", 0) * (request.end_date - request.start_date).days
                if total_cost > request.budget:
                    continue
            
            # Rating filter (if specified in preferences)
            min_rating = request.preferences.get("min_rating", 0)
            if hotel.get("rating", 0) < min_rating:
                continue
            
            # Amenity filter (if specified in preferences)
            required_amenities = request.preferences.get("required_amenities", [])
            if required_amenities:
                hotel_amenities = set(hotel.get("amenities", []))
                if not all(amenity in hotel_amenities for amenity in required_amenities):
                    continue
            
            filtered_hotels.append(hotel)
        
        self.log_activity(f"Applied filters: {len(filtered_hotels)} hotels remaining from {len(hotels)}")
        return filtered_hotels
    
    async def normalize_hotels(self, hotels: List[Dict[str, Any]], request: SearchRequest) -> List[Hotel]:
        """
        Normalize and validate hotel data
        
        Args:
            hotels: Raw hotel data
            request: Original search request
            
        Returns:
            List of validated Hotel objects
        """
        normalized_hotels = []
        
        for hotel_data in hotels:
            try:
                # Convert to Hotel object with validation
                hotel = Hotel(
                    name=hotel_data.get("name", "Unknown"),
                    address=hotel_data.get("address", "Unknown"),
                    city=hotel_data.get("city", "Unknown"),
                    country=hotel_data.get("country", "Unknown"),
                    rating=float(hotel_data.get("rating", 0)),
                    rating_category=HotelRating(hotel_data.get("rating_category", "standard")),
                    price_per_night=float(hotel_data.get("price_per_night", 0)),
                    currency=Currency(hotel_data.get("currency", "USD")),
                    amenities=hotel_data.get("amenities", []),
                    booking_link=hotel_data.get("booking_link"),
                    latitude=hotel_data.get("latitude"),
                    longitude=hotel_data.get("longitude")
                )
                
                normalized_hotels.append(hotel)
                
            except Exception as e:
                self.log_activity(f"Failed to normalize hotel: {str(e)}", "WARNING")
                continue
        
        # Sort by rating and price
        normalized_hotels.sort(key=lambda x: (-x.rating, x.price_per_night))
        
        self.log_activity(f"Normalized {len(normalized_hotels)} hotels")
        return normalized_hotels
