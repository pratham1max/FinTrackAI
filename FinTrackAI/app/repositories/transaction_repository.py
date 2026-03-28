from sqlalchemy import select, desc
from app.models.transaction import Transaction
from app.repositories.base import BaseRepository
from datetime import datetime

class TransactionRepository(BaseRepository):
    async def create(self, transaction_data):
        transaction = Transaction(**transaction_data)
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def get_all_by_user(self, user_id: int):
        result = await self.db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(desc(Transaction.date))
        )
        return result.scalars().all()

    async def get_by_id(self, transaction_id: int, user_id: int):
        result = await self.db.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, transaction_id: int, user_id: int):
        transaction = await self.get_by_id(transaction_id, user_id)
        if transaction:
            await self.db.delete(transaction)
            await self.db.commit()
            return True
        return False