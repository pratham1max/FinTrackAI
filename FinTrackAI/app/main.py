from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.routers.auth import router as auth_router
from app.routers.transactions import router as transactions_router
from app.routers.ai import router as ai_router
from app.routers.web import router as web_router
from app.routers.pages import router as pages_router

app = FastAPI(
    title="FinTrackAI",
    description="AI-Powered Personal Finance Tracker with Grok",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(transactions_router, prefix="/transactions", tags=["transactions"])
app.include_router(ai_router, prefix="/api", tags=["ai"])
app.include_router(web_router, tags=["web"])
app.include_router(pages_router, tags=["pages"])

@app.get("/")
async def root():
    return RedirectResponse("/dashboard")   # ← Changed to dashboard so you see the site immediately

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)