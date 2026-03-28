import os
from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
from langchain.prompts import ChatPromptTemplate
from app.core.config import settings
from app.models.transaction import Transaction
from sqlalchemy import text
import json

class AIService:
    def __init__(self, db):
        self.db = db
        self.client = AsyncOpenAI(
            api_key=settings.XAI_API_KEY,
            base_url="https://api.x.ai/v1"
        )
        self.llm = ChatOpenAI(
            model="grok-3",                    # or "grok-4" if available in 2026
            openai_api_key=settings.XAI_API_KEY,
            openai_api_base="https://api.x.ai/v1",
            temperature=0.7
        )
        # Embeddings (local + fast)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",    # works with Grok-compatible
            openai_api_key=settings.XAI_API_KEY,
            openai_api_base="https://api.x.ai/v1"
        )
        # PGVector connection for RAG
        self.vectorstore = PGVector(
            embeddings=self.embeddings,
            collection_name="transactions",
            connection_string=settings.DATABASE_URL.replace("+asyncpg", "+psycopg2"),
            use_jsonb=True
        )

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a transaction description"""
        response = await self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    async def auto_categorize(self, description: str, amount: float) -> str:
        """Grok-powered auto categorization"""
        prompt = f"""
        You are an expert finance assistant.
        Categorize this expense in ONE word (e.g. Food, Transport, Rent, Entertainment, Bills, Shopping, Health, Travel).
        Amount: {amount}
        Description: {description}
        Return ONLY the category name.
        """
        response = await self.client.chat.completions.create(
            model="grok-3",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20
        )
        return response.choices[0].message.content.strip()

    async def rag_chat(self, query: str, user_id: int) -> str:
        """Full RAG: retrieve similar transactions + Grok answer"""
        # Get user's transactions
        result = await self.db.execute(
            text("SELECT id, description, amount, category, date FROM transactions WHERE user_id = :user_id")
        )
        transactions = result.mappings().all()

        if not transactions:
            return "No transactions yet. Add some to start chatting!"

        # Vector search (pgvector magic)
        docs = [f"Amount: {t['amount']} | Desc: {t['description']} | Category: {t['category']} | Date: {t['date']}" 
                for t in transactions]
        
        # Retrieve top 5 similar
        retrieved = self.vectorstore.similarity_search(query, k=5, filter={"user_id": user_id})
        
        context = "\n".join([doc.page_content for doc in retrieved])
        
        prompt = ChatPromptTemplate.from_template("""
        You are a helpful financial advisor.
        Use only the following transaction history to answer the user's question.
        
        Transaction History:
        {context}
        
        Question: {question}
        
        Answer in a friendly, natural way. If you don't know, say so.
        """)
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"context": context, "question": query})
        return response.content

    async def store_transaction_embedding(self, transaction_id: int, description: str):
        """Called after every transaction create"""
        embedding = await self.generate_embedding(description)
        await self.db.execute(
            text("UPDATE transactions SET embedding = :embedding WHERE id = :id"),
            {"embedding": embedding, "id": transaction_id}
        )
        await self.db.commit()