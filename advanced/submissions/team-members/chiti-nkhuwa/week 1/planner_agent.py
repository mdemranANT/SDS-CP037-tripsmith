"""
Planner Agent (Controller) for TripSmith Multi-Agent Travel Planner
Orchestrates all specialized agents and creates complete travel itineraries
"""

import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import asyncio

from loguru import logger

from base_agent import BaseAgent
from flight_agent import FlightAgent
from hotel_agent import HotelAgent
from poi_agent import POIAgent
from schemas import (
    SearchRequest, AgentResponse, Itinerary, DailySchedule, Flight, Hotel, PointOfInterest,
    Currency
)


class PlannerAgent(BaseAgent):
    """Controller agent that orchestrates all specialized agents"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Planner Agent"""
        super().__init__("PlannerAgent", api_key)
        
        # Initialize specialized agents
        self.flight_agent = FlightAgent(api_key)
        self.hotel_agent = HotelAgent(api_key)
        self.poi_agent = POIAgent(api_key)
        
        self.log_activity("Planner Agent initialized successfully")
    
    async def process_request(self, request: SearchRequest) -> AgentResponse:
        """
        Process complete travel planning request
        
        Args:
            request: Search request with destination, dates, and preferences
            
        Returns:
            AgentResponse with complete itinerary
        """
        try:
            # Validate request
            if not self.validate_request(request):
                return self.create_response(
                    success=False,
                    error_message="Invalid search request"
                )
            
            self.log_activity(f"Processing complete travel plan for {request.destination}")
            
            # Step 1: Search for flights
            flight_response = await self.flight_agent.process_request(request)
            if not flight_response.success:
                self.log_activity("Flight search failed, continuing with mock data", "WARNING")
            
            # Step 2: Search for hotels
            hotel_response = await self.hotel_agent.process_request(request)
            if not hotel_response.success:
                self.log_activity("Hotel search failed, continuing with mock data", "WARNING")
            
            # Step 3: Search for POIs
            poi_response = await self.poi_agent.process_request(request)
            if not poi_response.success:
                self.log_activity("POI search failed, continuing with mock data", "WARNING")
            
            # Step 4: Create itinerary
            itinerary = await self.create_itinerary(
                request, 
                flight_response.data if flight_response.success else [],
                hotel_response.data if hotel_response.success else [],
                poi_response.data if poi_response.success else []
            )
            
            reasoning = f"Created complete itinerary for {request.destination} with flights, hotels, and activities"
            
            return self.create_response(
                success=True,
                data=itinerary,
                reasoning=reasoning
            )
            
        except Exception as e:
            self.log_activity(f"Travel planning failed: {str(e)}", "ERROR")
            return self.create_response(
                success=False,
                error_message=f"Travel planning error: {str(e)}"
            )
    
    async def create_itinerary(
        self,
        request: SearchRequest,
        flights: List[Flight],
        hotels: List[Hotel],
        pois: List[PointOfInterest]
    ) -> Itinerary:
        """
        Create a complete travel itinerary
        
        Args:
            request: Original search request
            flights: Available flights
            hotels: Available hotels
            pois: Available points of interest
            
        Returns:
            Complete Itinerary object
        """
        try:
            # Calculate trip duration
            trip_duration = (request.end_date - request.start_date).days
            
            # Select best flights
            selected_flights = self.select_best_flights(flights, request)
            
            # Select best hotels
            selected_hotels = self.select_best_hotels(hotels, request, trip_duration)
            
            # Create daily schedules
            daily_schedules = await self.create_daily_schedules(
                request, pois, trip_duration
            )
            
            # Create itinerary
            itinerary = Itinerary(
                trip_name=f"Trip to {request.destination}",
                destination=request.destination,
                start_date=request.start_date,
                end_date=request.end_date,
                total_days=trip_duration,
                outbound_flight=selected_flights.get("outbound"),
                return_flight=selected_flights.get("return"),
                hotels=selected_hotels,
                daily_schedules=daily_schedules,
                total_budget=request.budget,
                currency=request.currency
            )
            
            self.log_activity(f"Created itinerary with {len(selected_hotels)} hotels and {len(daily_schedules)} daily schedules")
            return itinerary
            
        except Exception as e:
            self.log_activity(f"Failed to create itinerary: {str(e)}", "ERROR")
            raise
    
    def select_best_flights(self, flights: List[Flight], request: SearchRequest) -> Dict[str, Optional[Flight]]:
        """
        Select the best flights for the trip
        
        Args:
            flights: Available flights
            request: Search request
            
        Returns:
            Dictionary with outbound and return flights
        """
        if not flights:
            return {"outbound": None, "return": None}
        
        # Sort flights by price and duration
        sorted_flights = sorted(flights, key=lambda x: (x.price, x.duration_minutes))
        
        # Select outbound flight (first day)
        outbound_flight = sorted_flights[0] if sorted_flights else None
        
        # For simplicity, use the same flight for return (in real scenario, would search for return flights)
        return_flight = sorted_flights[1] if len(sorted_flights) > 1 else outbound_flight
        
        self.log_activity(f"Selected flights: {outbound_flight.airline if outbound_flight else 'None'} outbound, {return_flight.airline if return_flight else 'None'} return")
        
        return {
            "outbound": outbound_flight,
            "return": return_flight
        }
    
    def select_best_hotels(self, hotels: List[Hotel], request: SearchRequest, trip_duration: int) -> List[Hotel]:
        """
        Select the best hotels for the trip
        
        Args:
            hotels: Available hotels
            request: Search request
            trip_duration: Number of nights
            
        Returns:
            List of selected hotels
        """
        if not hotels:
            return []
        
        # Filter by budget if specified
        if request.budget:
            max_hotel_budget = request.budget * 0.4  # Allocate 40% to hotels
            max_per_night = max_hotel_budget / trip_duration
            hotels = [h for h in hotels if h.price_per_night <= max_per_night]
        
        # Sort by rating and price
        sorted_hotels = sorted(hotels, key=lambda x: (-x.rating, x.price_per_night))
        
        # Select top 2 hotels for variety
        selected_hotels = sorted_hotels[:2] if len(sorted_hotels) >= 2 else sorted_hotels
        
        self.log_activity(f"Selected {len(selected_hotels)} hotels")
        return selected_hotels
    
    async def create_daily_schedules(
        self,
        request: SearchRequest,
        pois: List[PointOfInterest],
        trip_duration: int
    ) -> List[DailySchedule]:
        """
        Create daily schedules with activities
        
        Args:
            request: Search request
            pois: Available points of interest
            trip_duration: Number of days
            
        Returns:
            List of daily schedules
        """
        daily_schedules = []
        
        for day in range(trip_duration):
            current_date = request.start_date + timedelta(days=day)
            
            # Select activities for this day
            day_activities = self.select_activities_for_day(pois, day, trip_duration)
            
            # Create daily schedule
            daily_schedule = DailySchedule(
                date=current_date,
                activities=day_activities,
                free_time_slots=self.create_free_time_slots(day_activities),
                notes=self.generate_day_notes(day_activities, day, trip_duration)
            )
            
            daily_schedules.append(daily_schedule)
        
        self.log_activity(f"Created {len(daily_schedules)} daily schedules")
        return daily_schedules
    
    def select_activities_for_day(
        self,
        pois: List[PointOfInterest],
        day: int,
        trip_duration: int
    ) -> List[PointOfInterest]:
        """
        Select appropriate activities for a specific day
        
        Args:
            pois: Available points of interest
            day: Day number (0-indexed)
            trip_duration: Total trip duration
            
        Returns:
            List of activities for the day
        """
        if not pois:
            return []
        
        # Categorize POIs by type
        pois_by_category = {}
        for poi in pois:
            category = poi.category.value
            if category not in pois_by_category:
                pois_by_category[category] = []
            pois_by_category[category].append(poi)
        
        # Select activities based on day
        selected_activities = []
        
        # Day 0: Arrival day - lighter activities
        if day == 0:
            # Prefer food, entertainment, and light cultural activities
            for category in ["food", "entertainment", "cultural"]:
                if category in pois_by_category:
                    selected_activities.extend(pois_by_category[category][:1])
                    break
        
        # Last day: Departure day - lighter activities
        elif day == trip_duration - 1:
            # Prefer shopping, food, and light activities
            for category in ["shopping", "food", "cultural"]:
                if category in pois_by_category:
                    selected_activities.extend(pois_by_category[category][:1])
                    break
        
        # Middle days: Full activities
        else:
            # Mix of different activity types
            categories = list(pois_by_category.keys())
            for i, category in enumerate(categories):
                if i < 2:  # Select 2 activities per day
                    selected_activities.extend(pois_by_category[category][:1])
        
        # Limit to 3 activities per day
        return selected_activities[:3]
    
    def create_free_time_slots(self, activities: List[PointOfInterest]) -> List[Dict[str, Any]]:
        """
        Create free time slots based on activities
        
        Args:
            activities: Activities for the day
            
        Returns:
            List of free time slots
        """
        free_time_slots = []
        
        # Calculate total activity time
        total_activity_time = sum(activity.duration_hours or 2.0 for activity in activities)
        
        # Create free time slots
        if total_activity_time < 8:  # Less than 8 hours of activities
            remaining_time = 8 - total_activity_time
            
            if remaining_time >= 2:
                free_time_slots.append({
                    "start_time": "2:00 PM",
                    "end_time": "4:00 PM",
                    "description": "Free time for relaxation or exploration"
                })
            
            if remaining_time >= 4:
                free_time_slots.append({
                    "start_time": "6:00 PM",
                    "end_time": "8:00 PM",
                    "description": "Evening free time"
                })
        
        return free_time_slots
    
    def generate_day_notes(self, activities: List[PointOfInterest], day: int, trip_duration: int) -> str:
        """
        Generate notes for the day
        
        Args:
            activities: Activities for the day
            day: Day number
            trip_duration: Total trip duration
            
        Returns:
            Day notes
        """
        if day == 0:
            return "Arrival day - light activities to get oriented"
        elif day == trip_duration - 1:
            return "Departure day - packing and final activities"
        else:
            activity_types = [activity.category.value for activity in activities]
            return f"Full day of {', '.join(activity_types)} activities"
    
    async def validate_itinerary(self, itinerary: Itinerary) -> bool:
        """
        Validate the created itinerary
        
        Args:
            itinerary: Itinerary to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if all nights are covered by hotels
            if not itinerary.hotels:
                self.log_activity("Itinerary validation failed: no hotels", "WARNING")
                return False
            
            # Check if flights align with trip dates
            if itinerary.outbound_flight:
                flight_date = itinerary.outbound_flight.departure_time.date()
                if flight_date != itinerary.start_date:
                    self.log_activity("Itinerary validation failed: outbound flight date mismatch", "WARNING")
                    return False
            
            # Check if daily schedules are complete
            if len(itinerary.daily_schedules) != itinerary.total_days:
                self.log_activity("Itinerary validation failed: incomplete daily schedules", "WARNING")
                return False
            
            # Check budget constraints
            if itinerary.total_budget:
                total_cost = self.calculate_total_cost(itinerary)
                if total_cost > itinerary.total_budget:
                    self.log_activity(f"Itinerary validation failed: budget exceeded ({total_cost} > {itinerary.total_budget})", "WARNING")
                    return False
            
            self.log_activity("Itinerary validation passed")
            return True
            
        except Exception as e:
            self.log_activity(f"Itinerary validation error: {str(e)}", "ERROR")
            return False
    
    def calculate_total_cost(self, itinerary: Itinerary) -> float:
        """
        Calculate total cost of the itinerary
        
        Args:
            itinerary: Itinerary to calculate cost for
            
        Returns:
            Total cost
        """
        total_cost = 0.0
        
        # Flight costs
        if itinerary.outbound_flight:
            total_cost += itinerary.outbound_flight.price
        if itinerary.return_flight:
            total_cost += itinerary.return_flight.price
        
        # Hotel costs
        for hotel in itinerary.hotels:
            total_cost += hotel.price_per_night * itinerary.total_days
        
        # Activity costs (estimated)
        for daily_schedule in itinerary.daily_schedules:
            for activity in daily_schedule.activities:
                # Estimate activity cost based on price range
                if activity.price_range == "$":
                    total_cost += 20.0
                elif activity.price_range == "$$":
                    total_cost += 50.0
                elif activity.price_range == "$$$":
                    total_cost += 100.0
        
        return total_cost
    
    async def get_itinerary_summary(self, itinerary: Itinerary) -> Dict[str, Any]:
        """
        Generate a summary of the itinerary
        
        Args:
            itinerary: Itinerary to summarize
            
        Returns:
            Summary dictionary
        """
        total_cost = self.calculate_total_cost(itinerary)
        
        summary = {
            "trip_name": itinerary.trip_name,
            "destination": itinerary.destination,
            "duration": f"{itinerary.total_days} days",
            "total_cost": f"${total_cost:.2f}",
            "flights": {
                "outbound": itinerary.outbound_flight.airline if itinerary.outbound_flight else "None",
                "return": itinerary.return_flight.airline if itinerary.return_flight else "None"
            },
            "hotels": [hotel.name for hotel in itinerary.hotels],
            "total_activities": sum(len(schedule.activities) for schedule in itinerary.daily_schedules),
            "activity_categories": list(set(
                activity.category.value 
                for schedule in itinerary.daily_schedules 
                for activity in schedule.activities
            ))
        }
        
        return summary
