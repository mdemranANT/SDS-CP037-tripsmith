# 🔴 Advanced Track

Welcome to the **Advanced Track** of the TripSmith project! This track is designed for participants who want to explore **multi-agent AI systems** and push beyond simple tool-calling.  

You’ll build a **multi-agent travel planner** where different specialized agents (e.g., Flight Agent, Hotel Agent, Itinerary Agent) collaborate or compete to create the best possible itinerary. Along the way, you’ll practice advanced orchestration patterns, schema enforcement, and deployment strategies.

At the end of this track, you will:
- Design and implement **specialized agents** with distinct roles.  
- Use **Pydantic schemas** to standardize data across agents.  
- Explore **orchestration patterns** (centralized vs decentralized).  
- Deploy an advanced app with **Streamlit, Gradio, Huggingface Spaces**.  

---

## 🎓 Weekly Breakdown

### ✅ Week 1: Setup & Agent Foundations
- Create your repo, virtual environment, and `requirements.txt`.  
- Add a `.env` for API keys (`TAVILY_API_KEY`, `SERPAPI_API_KEY`, `OPENAI_API_KEY`).  
- Define **Pydantic schemas** for Flights, Hotels, POIs, and Itineraries.  
- Build initial **agents**:  
  - **Flight Agent** → searches flights and normalizes results.  
  - **Hotel Agent** → searches hotels with price and rating filters.  
  - **POI Agent** → gathers activities based on interests.  
- Add a **Controller (Planner)** that can query each agent and store results.  
- Implement **logging** to trace agent interactions.  

---

### ✅ Week 2: Multi-Agent Orchestration
- Experiment with **orchestration patterns**:  
  - **Centralized**: Planner agent queries all others and merges results.  
  - **Decentralized**: Agents propose options and negotiate (e.g., Hotel Agent rejects if budget exceeded).  
- Add **validation rules**:  
  - Ensure all nights are covered by hotels.  
  - Flights align with trip dates.  
  - Daily schedules balance activities and free time.  
- Add **reasoning steps**: Have agents explain why they chose or rejected certain options.  
- Support **structured JSON outputs** with combined results from all agents.  

---

### ✅ Week 3: Advanced Deployment

Choose your preferred deployment track:

#### 🟢 Beginner Track
- Build a **Streamlit or Gradio app**.
- Deploy directly to **Hugging Face Spaces** (no Docker required).
- Simple, fast, and ideal for quick sharing.

#### 🟡 Intermediate Track
- Build a **Streamlit or Gradio app**.
- **Dockerize** your application for reproducibility.
- Deploy the Docker container to **Huggingface Spaces** for more control over dependencies and environment.

#### 🔴 Advanced Track
- Build and containerize your app (Streamlit/Gradio or custom frontend).
- Deploy to a major cloud provider: **AWS, Azure, or GCP**.
- Use managed services (e.g., ECS, App Service, Cloud Run) for scalability, security, and advanced networking.


---

## 🗒️ Project Timeline Overview

| Phase                      | General Activities                                                      |
| -------------------------- | ----------------------------------------------------------------------- |
| **Week 1: Setup & Agents** | Repo, env, schemas, Flight/Hotel/POI agents, and Planner controller     |
| **Week 2: Orchestration**  | Multi-agent workflows, validation rules, reasoning, and CLI tool        |
| **Week 3: Deployment**     | Refine prompts, add fallback strategies, Streamlit/Gradio/HF deployment |

---

## 📃 Report Template

Use the [REPORT.md](./REPORT.md) to document your weekly progress, orchestration design decisions, and outputs (agent logs, JSON, screenshots of the app).

---

## 🚪 Where to Submit

Please place your work inside the appropriate folder:

* `submissions/team-members/your-name/` if you are part of the official project team
* `submissions/community-contributions/your-name/` if you are an external contributor

Refer to the [CONTRIBUTING.md](../CONTRIBUTING.md) for complete instructions.
