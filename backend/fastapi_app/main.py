'''
import subprocess
import sys
import pkg_resources
import os

def install_requirements():
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        print(f"Requirements file not found: {requirements_file}")
        return

    with open(requirements_file, "r") as f:
        required = f.read().splitlines()
    
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = [pkg for pkg in required if pkg.split("==")[0].lower() not in installed]

    if missing:
        print(f"Installing missing packages: {missing}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
    else:
        print("All required packages are already installed.")

    # PyTorch 설치
    try:
        import torch
    except ImportError:
        print("Installing PyTorch...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "torch"])

install_requirements()
'''
# FastAPI 앱의 진입점
from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from routers import brands, user_data, upload, convert
from routers import recommend, measurement

app = FastAPI()
'''
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://ec2-3-34-94-30.ap-northeast-2.compute.amazonaws.com:3000/"],  # React 개발 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brands.router)
app.include_router(user_data.router)

app.include_router(upload.router, prefix="/api")
app.include_router(convert.router)
'''

app.include_router(recommend.router)
app.include_router(measurement.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
