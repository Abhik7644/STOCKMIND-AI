from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
ALGORITHM  = os.getenv("ALGORITHM", "HS256")
EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain password — never store plain text."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Check if plain password matches stored hash."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    """
    Create a JWT token.
    Contains user id + expiry time.
    """
    to_encode = data.copy()
    expire    = datetime.utcnow() + timedelta(minutes=EXPIRE_MIN)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None