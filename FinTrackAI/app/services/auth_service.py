from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create_user(self, user_in: UserCreate):
        existing = await self.user_repo.get_by_email(user_in.email)
        if existing:
            raise ValueError("Email already registered")
        return await self.user_repo.create(user_in)

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)