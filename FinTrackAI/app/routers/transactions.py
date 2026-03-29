from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.transaction_service import TransactionService
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.models.user import User
from app.services.ai_service import AIService
import os

router = APIRouter()

# Setup templates
templates = Jinja2Templates(directory="app/templates")
def get_transaction_service(db: AsyncSession = Depends(get_db)):
    return TransactionService(db)

def get_ai_service(db: AsyncSession = Depends(get_db)):
    return AIService(db)

@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
    ai_service: AIService = Depends(get_ai_service)
):
    # Auto-categorize with Grok
    if not transaction.category:
        transaction.category = await ai_service.auto_categorize(transaction.description, transaction.amount)
    
    created = await service.create_transaction(transaction, current_user.id)
    
    # Store embedding for RAG
    await ai_service.store_transaction_embedding(created.id, created.description)
    
    return created

@router.get("/", response_model=list[TransactionResponse])
async def get_transactions(
    service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user)
):
    return await service.get_transactions(current_user.id)

@router.get("/html", response_class=HTMLResponse)
async def get_transactions_html(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transactions = await TransactionService(db).get_transactions(current_user.id)
    return templates.TemplateResponse("fragments/transactions.html", request=request, transactions=transactions)