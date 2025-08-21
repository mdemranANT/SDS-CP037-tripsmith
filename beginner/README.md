# 🟢 Beginner Track

Welcome to the **Beginner Track** of the TripSmith project! This track is designed for participants who want to build their first **Generative AI application** by creating a travel planner powered by APIs and an LLM.

You’ll build a **Python-based tool** that:
- Connects to APIs (Tavily or SerpAPI) to fetch **flights, hotels, and points of interest (POIs)**,  
- Uses an **LLM** to generate a **day-by-day itinerary**, and  
- Deploys your solution with **Streamlit** or **Gradio**.  

This track is beginner-friendly but still introduces you to real-world concepts like API integration, and deploying AI-powered apps.

---

## 🎓 Weekly Breakdown

### ✅ Week 1: Setup & Exploration
- Create your repo, virtual environment, and `requirements.txt` file.  
- Add a `.env` file for API keys (`TAVILY_API_KEY`, `SERPAPI_API_KEY`, `OPENAI_API_KEY`).  
- Implement **minimal API wrappers**:  
  - Flights → structured queries like `"origin to destination date best price"`.  
  - Hotels → search by location, price, and rating.  
  - POIs → search based on user interests.  

---

### ✅ Week 2: Itinerary Generation with LLM
- Prompt an LLM to take **user preferences + API results** and generate a structured itinerary.  
- Create a Markdown exporter to render the itinerary as a human-readable trip plan.  

---

### ✅ Week 3: Testing, Polish & Deployment
- Refine prompts for consistency (add constraints like budget, pace, and opening hours if available).
- Build a **Streamlit or Gradio app**:  
  - Form inputs for origin, destination, dates, budget, and interests.  
  - “Generate Plan” button → show itinerary per day with expandable sections.  
  - Buttons to download JSON/Markdown results.  

---

## 🗒️ Project Timeline Overview

| Phase                              | General Activities                                                  |
| ---------------------------------- | ------------------------------------------------------------------- |
| **Week 1: Setup & Exploration**    | Setup repo, environment, API wrappers, and caching                  |
| **Week 2: LLM Planning Pipeline**  | Use LLM to generate structured itineraries                          |
| **Week 3: Deployment**             | Testing, polishing prompts, and deploying with Streamlit or Gradio  |

---

## 📃 Report Template

Use the [REPORT.md](./REPORT.md) to document your weekly progress, code reasoning, and outputs (JSON + Markdown + screenshots of your app).

---

## 🚪 Where to Submit

Please place your work inside the appropriate folder:

- `submissions/team-members/your-name/` if you are part of the official project team  
- `submissions/community-contributions/your-name/` if you are an external contributor  

Refer to the [CONTRIBUTING.md](../CONTRIBUTING.md) for complete instructions.
