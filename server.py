import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)



import logging
from fastapi import FastAPI

import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown complete")

app.router.lifespan_context = lifespan

@app.get("/")
def read_root():
    logger.info("Root endpoint was accessed")
    return {"message": "Hello World"}

@app.get("/status")
def read_status():
    logger.info("Status endpoint was accessed")
    return {"status": "Server is running"}

@app.get("/status")
def read_status():
    logger.info("Status endpoint was accessed")
    return {"status": "Server is running"}