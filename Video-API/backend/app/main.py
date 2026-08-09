from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.analysis.video import router as video_router, limiter

# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="DeepTrace AI Engine",
    description="Multimodal Forensics & Deepfake Detection Platform",
    version="2.2"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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