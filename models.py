from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    age: Optional[int] = Field(None, ge=1, le=120, description="Возраст пользователя")
    is_subscribed: Optional[bool] = Field(False, description="Подписка на рассылку")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Alice",
                    "email": "alice@example.com",
                    "age": 30,
                    "is_subscribed": True
                }
            ]
        }
    }


class CommonHeaders(BaseModel):
    user_agent: str = Field(..., alias="User-Agent", description="User-Agent заголовок")
    accept_language: str = Field(..., alias="Accept-Language", description="Accept-Language заголовок")

    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, v: str) -> str
  
        pattern = r'^([a-zA-Z]{1,8}(-[a-zA-Z]{1,8})?(\s*;\s*q\s*=\s*(0(\.\d{1,3})?|1(\.0{1,3})?))?(\s*,\s*[a-zA-Z]{1,8}(-[a-zA-Z]{1,8})?(\s*;\s*q\s*=\s*(0(\.\d{1,3})?|1(\.0{1,3})?))?)*)*$'
        if not re.match(pattern, v):
            raise ValueError('Неверный формат Accept-Language')
        return v

    model_config = {
        "populate_by_name": True,
        "extra": "forbid"
    }
