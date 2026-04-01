from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import uuid
import time
from typing import Optional
from datetime import datetime, timezone

router = APIRouter(tags=["auth"])

SECRET_KEY = "your-secret-key-here-change-in-production"
serializer = URLSafeTimedSerializer(SECRET_KEY)

SESSION_LIFETIME = 300 
EXTEND_THRESHOLD = 180  

users_db = {
    "user123": {"password": "password123", "profile": {"username": "user123", "email": "user@example.com", "name": "Test User"}}
}


class LoginRequest(BaseModel):
    username: str
    password: str


def generate_session_token(user_id: str) -> str:
    """
    Генерирует подписанный токен сессии в формате: user_id.timestamp
    Использует itsdangerous для подписи
    """
    timestamp = int(time.time())
    data = f"{user_id}.{timestamp}"
    signed_data = serializer.dumps(data)
    return signed_data


def verify_session_token(token: str) -> tuple[Optional[str], Optional[int]]:
    """
    Проверяет подпись токена и возвращает (user_id, timestamp)
    Если подпись недействительна, возвращает (None, None)
    """
    try:
        data = serializer.loads(token, max_age=SESSION_LIFETIME)
        user_id, timestamp_str = data.split(".")
        timestamp = int(timestamp_str)
        return user_id, timestamp
    except (BadSignature, SignatureExpired, ValueError):
        return None, None


def should_extend_session(last_activity: int) -> bool:
    """
    Определяет, нужно ли продлить сессию
    Возвращает True, если прошло >= 3 минут и < 5 минут с последней активности
    """
    current_time = int(time.time())
    elapsed = current_time - last_activity
    return EXTEND_THRESHOLD <= elapsed < SESSION_LIFETIME


@router.post("/login")
async def login(login_data: LoginRequest, response: Response):
    """
    Задание 5.1, 5.2, 5.3: Маршрут входа
    Устанавливает подписанную cookie с токеном сессии
    """
    user = users_db.get(login_data.username)
    if not user or user["password"] != login_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user_id = login_data.username
    
    session_token = generate_session_token(user_id)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,  
        max_age=SESSION_LIFETIME,
        samesite="lax"
    )
    
    return {"message": "Login successful"}


@router.get("/profile")
async def get_profile(request: Request, response: Response):
    """
    Задание 5.1, 5.2, 5.3: Защищенный маршрут профиля
    Проверяет cookie и управляет временем жизни сессии
    """
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    
    user_id, timestamp = verify_session_token(session_token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    current_time = int(time.time())
    elapsed = current_time - timestamp
    
    if elapsed >= SESSION_LIFETIME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    
    if should_extend_session(timestamp):
        new_token = generate_session_token(user_id)
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            secure=False,
            max_age=SESSION_LIFETIME,
            samesite="lax"
        )
    
    user_data = users_db.get(user_id, {})
    profile = user_data.get("profile", {"username": user_id})
    
    return {
        "user_id": user_id,
        "profile": profile,
        "last_activity": datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat(),
        "session_valid_until": datetime.fromtimestamp(timestamp + SESSION_LIFETIME, tz=timezone.utc).isoformat()
    }


@router.post("/logout")
async def logout(response: Response):
    """Маршрут для выхода из системы - удаляет cookie"""
    response.delete_cookie("session_token", httponly=True)
    return {"message": "Logout successful"}
