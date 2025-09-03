"""
Main CLI tool for TripSmith Multi-Agent Travel Planner
Demonstrates the multi-agent system with example usage
"""

import os
import asyncio
import json
from datetime import date, datetime
from typing import Dict, Any

from dotenv import load_dotenv
from loguru import logger

from schemas import SearchRequest, Currency
from planner_agent import PlannerAgent


def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure loguru
    logger.remove()  # Remove default handler
    logger.add(
        "logs/tripsmith.log",
        rotation="1 day",
        retention="7 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}"
    )
    logger.add(
        lambda msg: print(msg, end=""),
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | {message}"
    )


def load_environment():
    """Load environment variables"""
    load_dotenv()
    
    # Check required API keys
    required_keys = ["OPENAI_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        logger.warning(f"Missing API keys: {missing_keys}")
        logger.warning("Some features may not work without proper API keys")
    
    return True


def create_sample_request() -> SearchRequest:
    """Create a sample search request for testing"""
    return SearchRequest(
        destination="Los Angeles",
        start_date=date(2024, 3, 15),
        end_date=date(2024, 3, 20),
        budget=2000.0,
        currency=Currency.USD,
        travelers=2,
        preferences={
            "interests": ["cultural", "outdoor", "food"],
            "min_rating": 3.5,
            "required_amenities": ["WiFi", "Parking"]
        }
    )


def create_custom_request() -> SearchRequest:
    """Create a custom search request from user input"""
    print("\n=== TripSmith Multi-Agent Travel Planner ===")
    print("Let's plan your perfect trip!\n")
    
    # Get destination
    destination = input("Destination (e.g., Los Angeles, Paris, Tokyo): ").strip()
    if not destination:
        destination = "Los Angeles"
    
    # Get dates
    try:
        start_date_str = input("Start date (YYYY-MM-DD, default: 2024-03-15): ").strip()
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else date(2024, 3, 15)
        
        end_date_str = input("End date (YYYY-MM-DD, default: 2024-03-20): ").strip()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else date(2024, 3, 20)
    except ValueError:
        logger.error("Invalid date format. Using default dates.")
        start_date = date(2024, 3, 15)
        end_date = date(2024, 3, 20)
    
    # Get budget
    try:
        budget_str = input("Budget in USD (default: 2000): ").strip()
        budget = float(budget_str) if budget_str else 2000.0
    except ValueError:
        logger.error("Invalid budget. Using default budget.")
        budget = 2000.0
    
    # Get travelers
    try:
        travelers_str = input("Number of travelers (default: 2): ").strip()
        travelers = int(travelers_str) if travelers_str else 2
    except ValueError:
        logger.error("Invalid number of travelers. Using default.")
        travelers = 2
    
    # Get interests
    interests_input = input("Interests (comma-separated, e.g., cultural,outdoor,food, default: cultural,outdoor,food): ").strip()
    interests = [interest.strip() for interest in interests_input.split(",")] if interests_input else ["cultural", "outdoor", "food"]
    
    return SearchRequest(
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        budget=budget,
        currency=Currency.USD,
        travelers=travelers,
        preferences={
            "interests": interests,
            "min_rating": 3.5,
            "required_amenities": ["WiFi"]
        }
    )


def display_itinerary_summary(summary: Dict[str, Any]):
    """Display itinerary summary in a formatted way"""
    print("\n" + "="*60)
    print("🎉 TRIP SUMMARY")
    print("="*60)
    print(f"📍 Destination: {summary['destination']}")
    print(f"📅 Duration: {summary['duration']}")
    print(f"💰 Total Cost: {summary['total_cost']}")
    print(f"✈️  Flights: {summary['flights']['outbound']} (outbound), {summary['flights']['return']} (return)")
    print(f"🏨 Hotels: {', '.join(summary['hotels'])}")
    print(f"🎯 Activities: {summary['total_activities']} total")
    print(f"🏷️  Activity Categories: {', '.join(summary['activity_categories'])}")
    print("="*60)


def display_detailed_itinerary(itinerary_data: Dict[str, Any]):
    """Display detailed itinerary information"""
    print("\n" + "="*60)
    print("📋 DETAILED ITINERARY")
    print("="*60)
    
    # Flight information
    if itinerary_data.get("outbound_flight"):
        flight = itinerary_data["outbound_flight"]
        print(f"\n✈️  OUTBOUND FLIGHT:")
        print(f"   Airline: {flight['airline']}")
        print(f"   Flight: {flight['flight_number']}")
        print(f"   From: {flight['departure_airport']} To: {flight['arrival_airport']}")
        print(f"   Departure: {flight['departure_time']}")
        print(f"   Arrival: {flight['arrival_time']}")
        print(f"   Duration: {flight['duration_minutes']} minutes")
        print(f"   Price: ${flight['price']}")
    
    # Hotel information
    if itinerary_data.get("hotels"):
        print(f"\n🏨 HOTELS:")
        for hotel in itinerary_data["hotels"]:
            print(f"   • {hotel['name']}")
            print(f"     Address: {hotel['address']}")
            print(f"     Rating: {hotel['rating']}/5 ({hotel['rating_category']})")
            print(f"     Price: ${hotel['price_per_night']}/night")
            print(f"     Amenities: {', '.join(hotel['amenities'])}")
    
    # Daily schedules
    if itinerary_data.get("daily_schedules"):
        print(f"\n📅 DAILY SCHEDULES:")
        for i, schedule in enumerate(itinerary_data["daily_schedules"], 1):
            print(f"\n   Day {i} - {schedule['date']}:")
            if schedule.get("activities"):
                for j, activity in enumerate(schedule["activities"], 1):
                    print(f"     {j}. {activity['name']}")
                    print(f"        Category: {activity['category']}")
                    print(f"        Duration: {activity['duration_hours']} hours")
                    print(f"        Rating: {activity['rating']}/5" if activity.get('rating') else "        Rating: N/A")
            if schedule.get("free_time_slots"):
                print(f"     Free Time:")
                for slot in schedule["free_time_slots"]:
                    print(f"       {slot['start_time']} - {slot['end_time']}: {slot['description']}")
            if schedule.get("notes"):
                print(f"     Notes: {schedule['notes']}")


async def main():
    """Main function to run the TripSmith multi-agent system"""
    try:
        # Setup
        setup_logging()
        load_environment()
        
        logger.info("Starting TripSmith Multi-Agent Travel Planner")
        
        # Create search request
        print("\nChoose request type:")
        print("1. Use sample request (Los Angeles, 5 days, $2000)")
        print("2. Create custom request")
        
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "2":
            request = create_custom_request()
        else:
            request = create_sample_request()
            logger.info("Using sample request")
        
        # Initialize planner agent
        logger.info("Initializing Planner Agent...")
        planner = PlannerAgent()
        
        # Process request
        logger.info(f"Processing travel request for {request.destination}")
        response = await planner.process_request(request)
        
        if response.success:
            logger.info("✅ Travel planning completed successfully!")
            
            # Get itinerary data
            itinerary = response.data
            
            # Display summary
            summary = await planner.get_itinerary_summary(itinerary)
            display_itinerary_summary(summary)
            
            # Display detailed itinerary
            itinerary_dict = itinerary.model_dump()
            display_detailed_itinerary(itinerary_dict)
            
            # Save to file
            output_file = f"itinerary_{request.destination.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(itinerary_dict, f, indent=2, default=str)
            
            logger.info(f"💾 Itinerary saved to {output_file}")
            
            # Validate itinerary
            is_valid = await planner.validate_itinerary(itinerary)
            if is_valid:
                logger.info("✅ Itinerary validation passed")
            else:
                logger.warning("⚠️  Itinerary validation failed")
            
        else:
            logger.error(f"❌ Travel planning failed: {response.error_message}")
            if response.reasoning:
                logger.info(f"Reasoning: {response.reasoning}")
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
