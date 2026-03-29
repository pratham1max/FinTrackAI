# FinTrackAI — AI-Powered Personal Finance Tracker

![FastAPI](https://img.shields.io/badge/FastAPI-0.115-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Tailwind](https://img.shields.io/badge/Tailwind-4.0-teal)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

**Live Demo**: [railway-link]  
**Stars**: (watch roll in)

## ✨ Features
- Professional dark-mode dashboard (Tailwind + DaisyUI)
- **RAG Chatbot** — asks questions about your entire financial history
- Async PostgreSQL + pgvector for semantic search
- JWT auth + clean architecture (repositories + services)
- Zero JavaScript frameworks — just HTMX

## Architecture
```mermaid
graph TD
    A[FastAPI Routers] --> B[Services]
    B --> C[Repositories]
    C --> D[(PostgreSQL + pgvector)]
    B --> E[LangChain]
    E --> D
    F[HTMX + Tailwind Dashboard] --> A
    G[AI Chat] --> E