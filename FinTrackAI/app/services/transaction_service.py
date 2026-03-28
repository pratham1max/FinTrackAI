from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreate, TransactionResponse

class TransactionService:
    def __init__(self, db):
        self.repo = TransactionRepository(db)

    async def create_transaction(self, transaction: TransactionCreate, user_id: int):
        data = transaction.model_dump()
        data["user_id"] = user_id
        # AI auto-categorization will be added in next step
        return await self.repo.create(data)

    async def get_transactions(self, user_id: int):
        return await self.repo.get_all_by_user(user_id)

    async def get_transaction(self, transaction_id: int, user_id: int):
        return await self.repo.get_by_id(transaction_id, user_id)

    async def delete_transaction(self, transaction_id: int, user_id: int):
        return await self.repo.delete(transaction_id, user_id)