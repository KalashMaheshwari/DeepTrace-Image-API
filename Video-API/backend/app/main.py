from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.analysis.video import router as video_router


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="DeepTrace AI Engine",
    description="Multimodal Forensics & Deepfake Detection Platform",
    version="2.1"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================



app.include_router(video_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def health_check():

    return {
        "system": "DeepTrace AI Engine",
        "status": "operational"
    }