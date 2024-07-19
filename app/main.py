from fastapi import FastAPI
from .routers import items
from .database import engine, Base

app = FastAPI()

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app.include_router(items.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI project"}
