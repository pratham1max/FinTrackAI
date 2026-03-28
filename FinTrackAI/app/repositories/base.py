from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class BaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db