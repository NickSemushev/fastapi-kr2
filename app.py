from fastapi import FastAPI
from products import router as products_router
from auth import router as auth_router
from headers import router as headers_router
from models import UserCreate
import uuid
import time

app = FastAPI(
    title="Контрольная работа №2",
    description="FastAPI приложение для контрольной работы",
    version="1.0.0"
)

app.include_router(products_router)
app.include_router(auth_router)
app.include_router(headers_router)


@app.post("/create_user", tags=["users"], response_model=UserCreate)
async def create_user(user: UserCreate):
    """
    Создание пользователя с валидацией данных
    """
    return user


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "FastAPI Контрольная работа №2",
        "endpoints": {
            "users": "/create_user (POST)",
            "products": "/products/{product_id} (GET), /products/search (GET)",
            "auth": "/login (POST), /profile (GET), /logout (POST)",
            "headers": "/headers (GET), /info (GET)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
