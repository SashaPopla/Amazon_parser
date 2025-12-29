import json
import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.parser import AmazonParser
from app.models import ProductSchema, CategorySchema

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(current_dir, "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "products.json"

def save_to_db(products: list):
    """Зберігає список у файл"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def load_from_db():
    """Читає список з файлу"""
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.post("/api/parse")
async def start_parsing(url: str):
    print(f"Start parsing: {url}")
    parser = AmazonParser()
    try:
        products = parser.parse_category(url)
        if not products:
            raise HTTPException(status_code=400, detail="Не вдалося отримати товари.")
        
        save_to_db(products)
        return {"status": "success", "count": len(products)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products", response_model=List[ProductSchema])
async def get_products(sort_by: str = "rank", min_rating: float = 0.0):
    products = load_from_db()
    
    filtered = []
    for p in products:
        try:
            r = float(p.get('rating', '0').replace(',', '.'))
        except:
            r = 0.0
        if r >= min_rating:
            filtered.append(p)

    if sort_by == "price":
        def get_price(item):
            try:
                clean = item['price'].replace('$', '').replace(',', '')
                return float(clean)
            except:
                return 999999.0
        filtered.sort(key=get_price)
    else:
        filtered.sort(key=lambda x: x['rank'])

    return filtered

@app.get("/api/categories")
async def get_categories():
    return [
        {"name": "Computers & Accessories", "url": "https://www.amazon.com/Best-Sellers-Computers-Accessories/zgbs/pc"},
        {"name": "Home & Kitchen", "url": "https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden"},
        {"name": "Video Games", "url": "https://www.amazon.com/Best-Sellers-Video-Games/zgbs/videogames"},
        {"name": "Books", "url": "https://www.amazon.com/best-sellers-books-Amazon/zgbs/books"}
    ]