from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from databases import Database
from pydantic import BaseModel

DATABASE_URL = "postgresql://myuser:mypassword@localhost/mydatabase"

# SQLAlchemy model
Base = declarative_base()

class ItemModel(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

# Pydantic model
class Item(BaseModel):
    id: int
    name: str
    description: str

# FastAPI app
app = FastAPI()

# Database engine
engine = create_engine(DATABASE_URL)

# Database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get the database connection
async def get_database():
    database = Database(DATABASE_URL)
    await database.connect()
    return database

# Create tables
Base.metadata.create_all(bind=engine)

# API endpoint to create an item
@app.post("/items/", response_model=Item)
async def create_item(item: Item, db: Session = Depends(get_db)):
    db_item = ItemModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# API endpoint to get all items
@app.get("/items/", response_model=list[Item])
async def read_items(database: Database = Depends(get_database)):
    query = "SELECT * FROM items"
    return await database.fetch_all(query)
