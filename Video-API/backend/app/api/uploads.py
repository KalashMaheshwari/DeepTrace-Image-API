import os

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.analysis.image_analysis import analyze_image
from pathlib import Path
import uuid
import shutil


router = APIRouter(
    prefix="/api",
    tags=["Media Upload"]
)


UPLOAD_DIR = Path("uploads/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_UPLOAD_DIR = Path("uploads/videos")

os.makedirs(VIDEO_UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".mov",
    ".avi",
    ".mp3",
    ".wav",
    ".m4a",
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".webm"
}


@router.post("/upload")
async def upload_media(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )

    original_extension = Path(file.filename).suffix.lower()

    if original_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {original_extension}"
        )

    file_id = str(uuid.uuid4())

    new_filename = f"{file_id}{original_extension}"
    if original_extension in {".mp4", ".avi", ".mov", ".mkv", ".webm"}:
        file_path = VIDEO_UPLOAD_DIR / new_filename
    else:   
        file_path = UPLOAD_DIR / new_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "success": True,
        "file_id": file_id,
        "original_filename": file.filename,
        "stored_filename": new_filename,
        "file_type": original_extension,
        "path": str(file_path)
    }