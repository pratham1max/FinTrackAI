import os
from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.core.config import settings
from app.models.transaction import Transaction
from sqlalchemy import text
import json
from sentence_transformers import SentenceTransformer

class AIService:
    def __init__(self, db):
        self.db = db
        self.client = AsyncOpenAI(
            api_key=settings.XAI_API_KEY,
            base_url="https://api.x.ai/v1"
        )
        self.llm = ChatOpenAI(
            model="grok-3",
            openai_api_key=settings.XAI_API_KEY,
            openai_api_base="https://api.x.ai/v1",
            temperature=0.7
        )
        # Use local embeddings model (sentence-transformers) instead of OpenAI
        self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a transaction description using local model"""
        embedding = self.embeddings_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

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

        # Generate embedding for query
        query_embedding = await self.generate_embedding(query)
        
        # Simple similarity search using cosine similarity
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        
        transaction_embeddings = []
        for t in transactions:
            emb = await self.generate_embedding(f"{t['description']} {t['category']}")
            transaction_embeddings.append(emb)
        
        # Calculate similarities
        similarities = cosine_similarity([query_embedding], transaction_embeddings)[0]
        top_indices = np.argsort(similarities)[-5:][::-1]  # Top 5
        
        # Build context from top similar transactions
        context_lines = []
        for idx in top_indices:
            t = transactions[idx]
            context_lines.append(f"Amount: ${t['amount']} | {t['description']} | Category: {t['category']} | Date: {t['date']}")
        
        context = "\n".join(context_lines)
        
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