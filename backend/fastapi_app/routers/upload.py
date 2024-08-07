import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import List

router = APIRouter()

UPLOAD_DIR = "uploaded_files"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    for file in files:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

    return {"info": "files uploaded successfully"}

@router.get("/files")
async def list_files():
    files = os.listdir(UPLOAD_DIR)
    return JSONResponse(content={"files": files})

@router.delete("/delete/{file_name}")
async def delete_file(file_name: str):
    file_name = unquote(file_name)  # URL 디코딩
    file_path = os.path.join(UPLOAD_DIR, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"info": f"file '{file_name}' deleted"}
    else:
        raise HTTPException(status_code=404, detail="File not found")
