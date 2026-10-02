from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine
from app.models import Hero, Team  # Quan trọng: Phải import để đăng ký model vào metadata

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tạo các bảng trong cơ sở dữ liệu khi khởi động ứng dụng
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Hello Hero API"}