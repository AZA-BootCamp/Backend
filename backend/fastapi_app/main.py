# FastAPI 앱의 진입점
from fastapi import FastAPI
# from routers import item_router

app = FastAPI()

# app.include_router(item_router.router)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
