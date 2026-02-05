import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import time
import logging

from database import get_db, Fruit as FruitModel, create_tables, test_connection
from redis_client import redis_client

class Fruit(BaseModel):
    name: str
    category: Optional[str] = None

class Fruits(BaseModel):
    fruits: List[Fruit]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Test database connection first
    if test_connection():
        # Create database tables on startup
        create_tables()
    else:
        print("❌ Failed to connect to database. Please check your DATABASE_URL.")
    yield
    # Cleanup code here (if needed)

app = FastAPI(debug=True, lifespan=lifespan)

origins = [
    "http://localhost:5173",
    # Add more origins here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/fruits", response_model=Fruits)
def get_fruits(db: Session = Depends(get_db)):
    start_time = time.time()
    
    # Try to get from cache first
    cache_key = "fruits:list"
    cached_fruits = redis_client.get(cache_key)
    
    if cached_fruits:
        end_time = time.time()
        logging.info(f"🚀 Cache hit! Retrieved fruits in {(end_time - start_time)*1000:.2f}ms")
        return Fruits(fruits=[Fruit(**fruit) for fruit in cached_fruits])
    
    # Cache miss - get from database
    fruits = db.query(FruitModel).all()
    fruit_list = []
    for fruit in fruits:
        fruit_data = {"name": fruit.name}
        if fruit.category is not None:
            fruit_data["category"] = fruit.category
        fruit_list.append(fruit_data)
    
    # Cache the result for 1 hour (3600 seconds)
    redis_client.set(cache_key, fruit_list, expire=3600)
    
    end_time = time.time()
    logging.info(f"🐘 Database query! Retrieved fruits in {(end_time - start_time)*1000:.2f}ms")
    
    return Fruits(fruits=[Fruit(**fruit_data) for fruit_data in fruit_list])

@app.post("/fruits")
def add_fruit(fruit: Fruit, db: Session = Depends(get_db)):
    # Check if fruit already exists
    existing_fruit = db.query(FruitModel).filter(FruitModel.name == fruit.name, FruitModel.category == fruit.category).first()
    if existing_fruit:
        raise HTTPException(status_code=400, detail="Fruit already exists")
    
    # Create new fruit
    db_fruit = FruitModel(name=fruit.name, category=fruit.category)
    db.add(db_fruit)
    db.commit()
    db.refresh(db_fruit)
    
    # Invalidate cache
    redis_client.delete("fruits:list")
    logging.info("🗑️ Cache invalidated after adding fruit")
    
    return fruit

@app.put("/fruits/{fruit_name}")
def update_fruit(fruit_name: str, fruit: Fruit, db: Session = Depends(get_db)):
    db_fruit = db.query(FruitModel).filter(FruitModel.name == fruit_name).first()
    if not db_fruit:
        raise HTTPException(status_code=404, detail="Fruit not found")
    db_fruit.name = fruit.name
    db_fruit.category = fruit.category
    db.commit()
    db.refresh(db_fruit)
    
    # Invalidate cache
    redis_client.delete("fruits:list")
    logging.info("🗑️ Cache invalidated after updating fruit")
    
    return fruit

@app.delete("/fruits/{fruit_name}")
def delete_fruit(fruit_name: str, db: Session = Depends(get_db)):
    fruit = db.query(FruitModel).filter(FruitModel.name == fruit_name).first()
    if not fruit:
        raise HTTPException(status_code=404, detail="Fruit not found")
    db.delete(fruit)
    db.commit()
    
    # Invalidate cache
    redis_client.delete("fruits:list")
    logging.info("🗑️ Cache invalidated after deleting fruit")
    
    return {"message": "Fruit deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)