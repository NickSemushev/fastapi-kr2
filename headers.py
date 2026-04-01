from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from datetime import datetime, timezone
from models import CommonHeaders

router = APIRouter(tags=["headers"])


async def get_headers(
    user_agent: str = None,
    accept_language: str = None,
    request: Request = None
) -> CommonHeaders:
    """
    Извлекает и валидирует заголовки User-Agent и Accept-Language
    """
    headers_data = {}
    
    if request:
        headers_data["User-Agent"] = request.headers.get("User-Agent")
        headers_data["Accept-Language"] = request.headers.get("Accept-Language")
    
    if not headers_data.get("User-Agent"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User-Agent header is required"
        )
    
    if not headers_data.get("Accept-Language"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Accept-Language header is required"
        )
    
    try:
        validated_headers = CommonHeaders(**headers_data)
        return validated_headers
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/headers")
async def get_headers_endpoint(
    headers_data: CommonHeaders = Depends(get_headers)
):
    """
    Задание 5.4: Маршрут /headers
    Возвращает заголовки User-Agent и Accept-Language
    """
    return {
        "User-Agent": headers_data.user_agent,
        "Accept-Language": headers_data.accept_language
    }


@router.get("/info")
async def get_info_endpoint(
    response: Response,
    headers_data: CommonHeaders = Depends(get_headers)
):
    """
    Задание 5.4: Маршрут /info
    Возвращает приветственное сообщение и заголовки,
    добавляет заголовок X-Server-Time
    """
    current_time = datetime.now(timezone.utc).isoformat()
    response.headers["X-Server-Time"] = current_time
    
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers_data.user_agent,
            "Accept-Language": headers_data.accept_language
        }
    }
