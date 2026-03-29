from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.ai_service import AIService
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

def get_ai_service(db: AsyncSession = Depends(get_db)) -> AIService:
    return AIService(db)

@router.post("/chat")
async def chat_with_grok(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)
):
    response = await ai_service.rag_chat(request.query, current_user.id)
    return {"response": response}