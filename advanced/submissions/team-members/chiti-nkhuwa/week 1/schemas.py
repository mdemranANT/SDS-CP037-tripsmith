"""
Pydantic schemas for TripSmith Multi-Agent Travel Planner
Defines data structures for flights, hotels, POIs, and itineraries
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class Currency(str, Enum):
    """Supported currencies"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"


class FlightClass(str, Enum):
    """Flight class options"""
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class HotelRating(str, Enum):
    """Hotel rating categories"""
    BUDGET = "budget"
    STANDARD = "standard"
    PREMIUM = "premium"
    LUXURY = "luxury"


class ActivityType(str, Enum):
    """Types of activities/POIs"""
    CULTURAL = "cultural"
    OUTDOOR = "outdoor"
    FOOD = "food"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    HISTORICAL = "historical"
    NATURE = "nature"


class Flight(BaseModel):
    """Flight information schema"""
    airline: str = Field(..., description="Airline name")
    flight_number: str = Field(..., description="Flight number")
    departure_airport: str = Field(..., description="Departure airport code")
    arrival_airport: str = Field(..., description="Arrival airport code")
    departure_time: datetime = Field(..., description="Departure date and time")
    arrival_time: datetime = Field(..., description="Arrival date and time")
    duration_minutes: int = Field(..., description="Flight duration in minutes")
    price: float = Field(..., description="Flight price")
    currency: Currency = Field(default=Currency.USD, description="Price currency")
    flight_class: FlightClass = Field(default=FlightClass.ECONOMY, description="Flight class")
    stops: int = Field(default=0, description="Number of stops")
    booking_link: Optional[str] = Field(None, description="Booking URL")
    
    @validator('duration_minutes')
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError('Duration must be positive')
        return v
    
    @validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Price cannot be negative')
        return v


class Hotel(BaseModel):
    """Hotel information schema"""
    name: str = Field(..., description="Hotel name")
    address: str = Field(..., description="Hotel address")
    city: str = Field(..., description="City")
    country: str = Field(..., description="Country")
    rating: float = Field(..., ge=0, le=5, description="Hotel rating (0-5)")
    rating_category: HotelRating = Field(..., description="Hotel category")
    price_per_night: float = Field(..., description="Price per night")
    currency: Currency = Field(default=Currency.USD, description="Price currency")
    amenities: List[str] = Field(default_factory=list, description="Available amenities")
    booking_link: Optional[str] = Field(None, description="Booking URL")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    
    @validator('rating')
    def validate_rating(cls, v):
        if not 0 <= v <= 5:
            raise ValueError('Rating must be between 0 and 5')
        return v


class PointOfInterest(BaseModel):
    """Point of Interest schema"""
    name: str = Field(..., description="POI name")
    description: str = Field(..., description="POI description")
    category: ActivityType = Field(..., description="Activity type")
    address: Optional[str] = Field(None, description="POI address")
    city: str = Field(..., description="City")
    country: str = Field(..., description="Country")
    rating: Optional[float] = Field(None, ge=0, le=5, description="POI rating (0-5)")
    price_range: Optional[str] = Field(None, description="Price range (e.g., '$', '$$', '$$$')")
    duration_hours: Optional[float] = Field(None, description="Typical visit duration in hours")
    opening_hours: Optional[str] = Field(None, description="Opening hours information")
    website: Optional[str] = Field(None, description="Official website")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    
    @validator('duration_hours')
    def validate_duration(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Duration must be positive')
        return v


class DailySchedule(BaseModel):
    """Daily itinerary schedule"""
    date: date = Field(..., description="Schedule date")
    activities: List[PointOfInterest] = Field(default_factory=list, description="Planned activities")
    free_time_slots: List[Dict[str, Any]] = Field(default_factory=list, description="Free time periods")
    notes: Optional[str] = Field(None, description="Additional notes for the day")
    
    @validator('activities')
    def validate_activities(cls, v):
        # Ensure activities don't overlap significantly
        # This is a simplified validation - could be enhanced
        return v


class Itinerary(BaseModel):
    """Complete travel itinerary"""
    trip_name: str = Field(..., description="Trip name/description")
    destination: str = Field(..., description="Main destination")
    start_date: date = Field(..., description="Trip start date")
    end_date: date = Field(..., description="Trip end date")
    total_days: int = Field(..., description="Total trip duration in days")
    
    # Travel components
    outbound_flight: Optional[Flight] = Field(None, description="Outbound flight")
    return_flight: Optional[Flight] = Field(None, description="Return flight")
    hotels: List[Hotel] = Field(default_factory=list, description="Booked hotels")
    
    # Daily schedules
    daily_schedules: List[DailySchedule] = Field(default_factory=list, description="Daily itineraries")
    
    # Budget information
    total_budget: Optional[float] = Field(None, description="Total trip budget")
    currency: Currency = Field(default=Currency.USD, description="Budget currency")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('total_days')
    def validate_total_days(cls, v, values):
        if 'start_date' in values and 'end_date' in values:
            expected_days = (values['end_date'] - values['start_date']).days + 1
            if v != expected_days:
                raise ValueError(f'Total days should be {expected_days}, got {v}')
        return v


class AgentResponse(BaseModel):
    """Standard response format for all agents"""
    agent_name: str = Field(..., description="Name of the responding agent")
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    reasoning: Optional[str] = Field(None, description="Agent's reasoning for decisions")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class SearchRequest(BaseModel):
    """Standard search request format"""
    destination: str = Field(..., description="Destination city/country")
    start_date: date = Field(..., description="Trip start date")
    end_date: date = Field(..., description="Trip end date")
    budget: Optional[float] = Field(None, description="Total budget")
    currency: Currency = Field(default=Currency.USD, description="Budget currency")
    travelers: int = Field(default=1, description="Number of travelers")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    
    @validator('travelers')
    def validate_travelers(cls, v):
        if v < 1:
            raise ValueError('Number of travelers must be at least 1')
        return v
