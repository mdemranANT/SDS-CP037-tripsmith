# TripSmith Multi-Agent Travel Planner - Week 1

## 🎯 **Project Overview**

This is Week 1 of the **Advanced Track** TripSmith project, focusing on building a **multi-agent AI system** for travel planning. The system consists of specialized agents that collaborate to create comprehensive travel itineraries.

## 🏗️ **Architecture**

### **Multi-Agent System Design**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flight Agent  │    │   Hotel Agent   │    │   POI Agent     │
│                 │    │                 │    │                 │
│ • Searches      │    │ • Searches      │    │ • Searches      │
│   flights       │    │   hotels        │    │   activities    │
│ • Normalizes    │    │ • Applies       │    │ • Categorizes   │
│   results       │    │   filters       │    │   by interests  │
│ • Validates     │    │ • Validates     │    │ • Validates     │
│   data          │    │   data          │    │   data          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Planner Agent   │
                    │ (Controller)    │
                    │                 │
                    │ • Orchestrates  │
                    │   all agents    │
                    │ • Creates       │
                    │   itineraries   │
                    │ • Validates     │
                    │   results       │
                    └─────────────────┘
```

### **Agent Responsibilities**

| Agent | Purpose | Key Features |
|-------|---------|-------------|
| **Flight Agent** | Flight search and booking | • Multi-API search (Tavily, SerpAPI)<br>• Flight normalization<br>• Price/duration ranking |
| **Hotel Agent** | Hotel search and filtering | • Price/rating filters<br>• Amenity matching<br>• Budget allocation |
| **POI Agent** | Activities and attractions | • Interest-based search<br>• Category classification<br>• Duration estimation |
| **Planner Agent** | Orchestration and planning | • Multi-agent coordination<br>• Itinerary creation<br>• Validation and optimization |

## 📁 **Project Structure**

```
week1/
├── requirements.txt          # Dependencies
├── env_example.txt           # Environment variables template
├── schemas.py               # Pydantic data models
├── base_agent.py            # Base agent class
├── flight_agent.py          # Flight search agent
├── hotel_agent.py           # Hotel search agent
├── poi_agent.py             # Points of interest agent
├── planner_agent.py         # Main orchestrator agent
├── main.py                  # CLI interface
├── README.md               # This file
└── logs/                   # Log files (created at runtime)
```

## 🚀 **Quick Start**

### **1. Environment Setup**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. API Keys Setup**

Create a `.env` file based on `env_example.txt`:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (for enhanced functionality)
TAVILY_API_KEY=your_tavily_api_key_here
SERPAPI_API_KEY=your_serpapi_api_key_here
```

### **3. Run the System**

```bash
python main.py
```

## 🎮 **Usage Examples**

### **Sample Request**
```python
from schemas import SearchRequest, Currency
from datetime import date

request = SearchRequest(
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
```

### **Individual Agent Usage**
```python
from flight_agent import FlightAgent
from hotel_agent import HotelAgent
from poi_agent import POIAgent

# Initialize agents
flight_agent = FlightAgent()
hotel_agent = HotelAgent()
poi_agent = POIAgent()

# Use individual agents
flight_response = await flight_agent.process_request(request)
hotel_response = await hotel_agent.process_request(request)
poi_response = await poi_agent.process_request(request)
```

### **Complete Planning**
```python
from planner_agent import PlannerAgent

# Initialize planner (orchestrates all agents)
planner = PlannerAgent()

# Get complete itinerary
response = await planner.process_request(request)
itinerary = response.data
```

## 📊 **Data Schemas**

### **Core Data Models**

- **`Flight`**: Airline, flight number, airports, times, price, class
- **`Hotel`**: Name, address, rating, price, amenities, coordinates
- **`PointOfInterest`**: Name, description, category, rating, duration
- **`DailySchedule`**: Date, activities, free time, notes
- **`Itinerary`**: Complete trip with flights, hotels, schedules

### **Validation Rules**

- Flight dates align with trip dates
- Hotel coverage for all nights
- Activity duration limits per day
- Budget constraints across all components
- Rating and amenity filters

## 🔧 **Key Features**

### **Multi-Agent Orchestration**
- **Centralized Control**: Planner agent coordinates all specialized agents
- **Parallel Processing**: Agents can work simultaneously
- **Error Handling**: Graceful degradation when individual agents fail
- **Logging**: Comprehensive activity tracking across all agents

### **Data Standardization**
- **Pydantic Schemas**: Type-safe data validation
- **Normalization**: Consistent data formats across APIs
- **Validation**: Business rule enforcement
- **Serialization**: JSON export capabilities

### **Search Capabilities**
- **Multi-API Support**: Tavily, SerpAPI, with fallbacks
- **LLM Integration**: OpenAI for data extraction and generation
- **Mock Data**: Fallback when APIs are unavailable
- **Caching**: Efficient result reuse

### **Intelligent Planning**
- **Budget Allocation**: Smart distribution across components
- **Activity Scheduling**: Balanced daily itineraries
- **Preference Matching**: Interest-based activity selection
- **Validation**: Comprehensive itinerary verification

## 📈 **Performance & Scalability**

### **Optimization Features**
- **Async Processing**: Non-blocking agent operations
- **Concurrent Searches**: Parallel API calls
- **Result Caching**: Avoid redundant API calls
- **Error Recovery**: Fallback strategies

### **Monitoring & Logging**
- **Structured Logging**: JSON-formatted logs with rotation
- **Agent Activity Tracking**: Individual agent performance
- **Error Reporting**: Detailed error messages and reasoning
- **Performance Metrics**: Response times and success rates

## 🧪 **Testing**

### **Unit Tests**
```bash
# Run tests (when implemented)
pytest tests/
```

### **Integration Tests**
```bash
# Test complete workflow
python main.py
```

### **Mock Data Testing**
The system includes comprehensive mock data for testing without API keys.

## 🔮 **Week 1 Achievements**

✅ **Completed Tasks**
- [x] Project structure and dependencies
- [x] Pydantic schemas for data validation
- [x] Base agent class with common functionality
- [x] Flight Agent with search and normalization
- [x] Hotel Agent with filtering and ranking
- [x] POI Agent with categorization and interests
- [x] Planner Agent for orchestration
- [x] CLI interface for testing
- [x] Comprehensive logging system
- [x] Error handling and fallbacks

## 🚧 **Known Limitations**

### **Current Constraints**
- **API Dependencies**: Requires external API keys for full functionality
- **Mock Data**: Limited to predefined scenarios
- **Search Depth**: Basic search depth for performance
- **Real-time Data**: Not real-time (uses cached/mock data)

### **Future Enhancements**
- **Real-time APIs**: Integration with live booking systems
- **Advanced Filtering**: More sophisticated preference matching
- **Machine Learning**: Predictive pricing and recommendations
- **User Interface**: Web-based UI for better UX

## 📚 **API Documentation**

### **Required APIs**
- **OpenAI**: LLM processing and data extraction
- **Tavily**: Web search for travel information
- **SerpAPI**: Additional search capabilities

### **Optional APIs**
- **Google Maps**: Enhanced location data
- **Amadeus**: Professional flight/hotel data

## 🤝 **Contributing**

1. Follow the established code structure
2. Add comprehensive logging for new features
3. Include error handling and fallbacks
4. Update schemas for new data types
5. Test with both real and mock data

## 📄 **License**

This project is part of the SuperDataScience Community Project.

---

**Next Steps**: Week 2 will focus on advanced orchestration patterns, validation rules, and reasoning steps.
