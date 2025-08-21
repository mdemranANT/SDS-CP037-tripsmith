# Welcome to the SuperDataScience Community Project!

Welcome to the **TripSmith: Building an AI-Powered Travel Planner** repository! 🎉

This project is a collaborative initiative brought to you by SuperDataScience, a global learning community focused on data science, machine learning, and AI. Whether you’re starting with Generative AI or looking to deepen your skills with tool-using LLMs, we’re excited to have you on board!

To contribute to this project, please follow the steps outlined in our [CONTRIBUTING.md](./CONTRIBUTING.md) file.

---

## 📂 Repository Structure

This project supports two tracks based on experience level:

```

project-name/
├── beginner/                 ← Beginner track files
│   ├── README.md             ← Scope of Works for Beginner Track
│   ├── REPORT.md             ← Markdown template for beginner submissions
│   └── submissions/
│       ├── team-members/
│       └── community-contributions/
│
├── advanced/                 ← Advanced track files
│   ├── README.md             ← Scope of Works for Advanced Track
│   ├── REPORT.md             ← Markdown template for advanced submissions
│   └── submissions/
│       ├── team-members/
│       └── community-contributions/
│
├── CONTRIBUTING.md
├── requirements.txt
└── README.md                 ← You are here!

```

---

## 🟢 Beginner Track

The **Beginner Track** focuses on building a **Python-based travel planner** that connects to APIs (Tavily or SerpAPI) to fetch **flights, hotels, and points of interest (POIs)**. Using an LLM, you will synthesize this information into a simple **day-by-day itinerary**.

At the end of the track, you will:
- Build minimal API wrappers for search queries.
- Prompt an LLM to generate an itinerary in JSON and Markdown formats.
- Deploy your solution with **Streamlit** or **Gradio**.

📌 Get started:  
➡️ [Beginner Track Scope of Works](./beginner/README.md)  
➡️ [Beginner Report Template](./beginner/REPORT.md)  
➡️ [Submit your work](./beginner/submissions/)  

---

## 🔴 Advanced Track

The **Advanced Track** challenges participants to design a **multi-agent AI planner** with advanced reasoning. You will explore concepts like:
- **Specialized agents** (Flight Agent, Hotel Agent, Itinerary Agent).
- **Orchestration patterns** (central planner vs decentralized negotiation).
- **Use schemas** (via Pydantic) to structure flight, hotel, and POI data.
- **Deployment enhancements** (Hugging Face Spaces, Dockerized apps, advanced Streamlit/Gradio dashboards).

At the end of the track, you will have a **multi-agent travel planning system** that goes beyond simple tool-calling and introduces advanced AI engineering practices.


📌 Get started:  
➡️ [Advanced Track Scope of Works](./advanced/README.md)  
➡️ [Advanced Report Template](./advanced/REPORT.md)  
➡️ [Submit your work](./advanced/submissions/)  

---

## 🌍 APIs & Tools

This project relies on live web data via APIs.  
- **Search APIs**: [Tavily](https://tavily.com/) or [SerpAPI](https://serpapi.com/)  
- **LLMs**: OpenAI GPT models (or any provider supporting function/tool calling)  
- **Deployment**: [Streamlit](https://streamlit.io/) or [Gradio](https://www.gradio.app/)  

---

## 🗒️ Project Timeline Overview

| Phase                                        | General Activities                                                                 |
| -------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Week 1: Setup + Exploration**              | Repo setup, API wrappers, schemas, and mock data                                   |
| **Week 2: LLM Planning Pipeline**            | LLM prompts, JSON schema outputs, itinerary generation, CLI tool                   |
| **Week 3: Streamlit/Gradio + Deployment**    | Testing, validation, and deployment via Streamlit/Gradio                           |


---

## 🙌 Contributions & Community

This project is open to both official team members and outside community contributors.

* 🧑‍💻 **Team Members** should submit their work under `team-members/`  
* 🌍 **Community Contributors** are welcome to fork the repo and submit under `community-contributions/`  

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on how to participate.
