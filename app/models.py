from typing import List, Optional
from pydantic import BaseModel

class CategorySchema(BaseModel):
    name: str
    url: str

class ProductSchema(BaseModel):
    asin: str
    title: str
    rank: int
    price: str
    currency: str = "$"
    list_price: Optional[str] = None
    discount_percent: Optional[str] = None
    rating: Optional[str] = None
    reviews_count: Optional[str] = None
    is_prime: bool = False
    best_sellers_rank: Optional[str] = None
    bullet_points: List[str] = []
    main_image_url: str
    product_url: str