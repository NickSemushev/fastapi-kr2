from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/products", tags=["products"])

sample_products = [
    {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99},
    {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99},
]


class ProductResponse(BaseModel):
    product_id: int
    name: str
    category: str
    price: float


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """Получение продукта по ID"""
    for product in sample_products:
        if product["product_id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    keyword: str = Query(..., description="Ключевое слово для поиска"),
    category: Optional[str] = Query(None, description="Категория для фильтрации"),
    limit: int = Query(10, ge=1, le=50, description="Максимальное количество товаров")
):
    """Поиск продуктов по ключевому слову и категории"""
    results = []
    keyword_lower = keyword.lower()
    
    for product in sample_products:
        if keyword_lower not in product["name"].lower():
            continue
        if category and product["category"].lower() != category.lower():
            continue
        results.append(product)
    
    return results[:limit]
