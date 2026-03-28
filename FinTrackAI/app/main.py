from app.routers.pages import router as pages_router
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.core.database import engine, Base
from app.routers import auth, transactions

app = FastAPI(
    title="FinTrackAI",
    description="AI-Powered Personal Finance Tracker with Grok RAG Chatbot",
    version="1.0.0"
)

# Mount static & templates (we'll use them soon)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(pages_router, tags=["pages"])

@app.get("/")
async def root():
    return {"message": "FinTrackAI API is running! 🚀 Visit /docs"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)