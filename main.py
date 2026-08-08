import io
import base64
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import PIL.ExifTags

from aide_wrapper import AIDEInferenceEngine

app = FastAPI(
    title="DeepTrace AI Engine",
    description="Explainable Media Forensics Platform powered by AIDE (ICLR 2025)",
    version="4.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AIDE Model Engine
aide_engine = AIDEInferenceEngine(checkpoint_path="weights/aide_checkpoint.pth")

def extract_metadata(image: Image.Image) -> dict:
    """Extracts EXIF metadata and inspects for synthetic/editing signatures."""
    exif_data = {}
    ai_software_detected = False
    software_name = "None"

    try:
        raw_exif = image._getexif()
        if raw_exif:
            for tag_id, value in raw_exif.items():
                tag = PIL.ExifTags.TAGS.get(tag_id, tag_id)
                exif_data[str(tag)] = str(value)
                
                if tag == "Software":
                    software_name = str(value)
                    if any(sig in software_name.lower() for sig in ["photoshop", "midjourney", "gimp", "stable", "dall-e", "flux"]):
                        ai_software_detected = True
    except Exception:
        pass

    return {
        "has_exif_headers": bool(exif_data),
        "software_signature": software_name,
        "editing_software_detected": ai_software_detected,
        "format": image.format,
        "dimensions": f"{image.width}x{image.height}",
        "raw_exif_summary": dict(list(exif_data.items())[:5]) if exif_data else "No EXIF headers found"
    }

@app.get("/")
def health_check():
    return {
        "system": "DeepTrace AI Engine",
        "model_architecture": "AIDE (ICLR 2025)",
        "status": "operational"
    }

@app.post("/api/v1/analyze")
async def analyze_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # 1. Metadata Forensics
        metadata_analysis = extract_metadata(image)

        # 2. AIDE Dual-Branch Neural Inference
        raw_output = aide_engine.predict(image)
        
        raw_fake_probability = 50.0
        if isinstance(raw_output, list) and len(raw_output) > 0 and len(raw_output[0]) == 2:
            import torch
            logits = torch.tensor(raw_output[0])
            prob = torch.softmax(logits, dim=-1)[1].item()
            raw_fake_probability = round(prob * 100.0, 2)
        elif isinstance(raw_output, float) or isinstance(raw_output, int):
            raw_fake_probability = float(raw_output)

        # 3. Dynamic Ensemble Penalties
        heuristic_penalty = 0.0
        if not metadata_analysis["has_exif_headers"]:
            heuristic_penalty += 15.0
        
        w, h = image.width, image.height
        if w == h or metadata_analysis["dimensions"] in ["1024x1024", "512x512", "447x447"]:
            heuristic_penalty += 10.0

        # Composite Risk Calculation
        composite_synthetic_risk = min(100.0, round(raw_fake_probability + heuristic_penalty, 2))
        
        SYNTHETIC_THRESHOLD = 30.0
        is_synthetic = composite_synthetic_risk >= SYNTHETIC_THRESHOLD

        return {
            "app_name": "DeepTrace AI Premium",
            "filename": file.filename,
            "verdict": "MANIPULATED / SYNTHETIC" if is_synthetic else "AUTHENTIC MEDIA",
            "confidence_score": composite_synthetic_risk,
            "is_synthetic": is_synthetic,
            "analysis_breakdown": {
                "neural_model_probabilities": {
                    "aide_raw_fake_probability": f"{raw_fake_probability}%",
                    "heuristic_risk_penalty": f"+{heuristic_penalty}%",
                    "final_composite_synthetic_risk": f"{composite_synthetic_risk}%",
                    "threshold_applied": f"{SYNTHETIC_THRESHOLD}%"
                },
                "forensic_metadata": metadata_analysis
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepTrace execution failed: {str(e)}")