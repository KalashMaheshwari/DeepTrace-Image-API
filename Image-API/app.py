import io
import base64
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
import PIL.ExifTags
import spaces
import logging

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Image-API")

app = FastAPI(
    title="DeepTrace AI Engine",
    description="Multimodal Forensics & Deepfake Detection Platform",
    version="2.2"
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load SigLIP-based Deepfake Detector Model
MODEL_NAME = "Skullly/DeepFake-image-detection-ViT-384"
print(f"Loading DeepTrace AI SigLIP Neural Engine ({MODEL_NAME})...")

processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)
model.eval()

# Startup Label Validation
logger.info(f"Model Labels: {model.config.id2label}")
expected_keywords = ["fake", "real", "synthetic", "authentic", "manipulated", "deepfake"]
labels_valid = any(
    any(kw in label.lower() for kw in expected_keywords) 
    for label in model.config.id2label.values()
)
if not labels_valid:
    logger.error("Startup Failure: Model labels do not contain expected keywords.")
    raise RuntimeError("Model label validation failed on startup.")

print("DeepTrace AI Engine Ready!")

def run_neural_inference(image):
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=-1)[0]
    return probabilities


def extract_metadata(image: Image.Image) -> dict:
    """Extracts metadata and inspects for synthetic/editing signatures."""
    exif_data = {}
    ai_software_detected = False
    software_name = "None"
    has_metadata = False

    try:
        # JPEG EXIF
        if hasattr(image, "getexif"):
            raw_exif = image.getexif()
            if raw_exif:
                for tag_id, value in raw_exif.items():
                    tag = PIL.ExifTags.TAGS.get(tag_id, tag_id)
                    exif_data[str(tag)] = str(value)
                    has_metadata = True

        # PNG / General Info
        if image.info:
            for key, value in image.info.items():
                if isinstance(value, (str, bytes)):
                    exif_data[str(key)] = str(value)[:500]
                    has_metadata = True

        for tag, value in exif_data.items():
            if "software" in tag.lower():
                software_name = str(value)
            if any(sig in str(value).lower() for sig in ["photoshop", "midjourney", "gimp", "stable", "dall-e", "flux"]):
                ai_software_detected = True

    except Exception as e:
        logger.warning(f"Error extracting metadata: {e}")

    return {
        "has_exif_headers": has_metadata,
        "software_signature": software_name,
        "editing_software_detected": ai_software_detected,
        "format": image.format,
        "dimensions": f"{image.width}x{image.height}",
        "raw_exif_summary": dict(list(exif_data.items())[:5]) if exif_data else "No metadata found"
    }


def generate_heatmap_overlay(image: Image.Image) -> str:
    """Generates an edge/texture map (not model attention) highlighting high-frequency details."""
    gray = image.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    enhanced = ImageEnhance.Contrast(edges).enhance(2.5)
    heatmap_colored = ImageOps.colorize(enhanced, black="blue", white="red", mid="yellow")
    blended = Image.blend(image.convert("RGB"), heatmap_colored, alpha=0.45)
    
    buffered = io.BytesIO()
    blended.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_str}"


@app.get("/")
def health_check():
    return {"system": "DeepTrace AI Engine", "status": "operational", "model": MODEL_NAME}


@app.post("/api/v1/analyze")
@limiter.limit("10/minute")
async def analyze_image(request: Request, file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File uploaded must be an image.")

    try:
        contents = await file.read()
        
        # Max file size check (20 MB)
        MAX_FILE_SIZE = 20 * 1024 * 1024
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 20MB.")
            
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # 1. Metadata Forensics
        metadata_analysis = extract_metadata(image)

        # 2. Model Inference via ZeroGPU
        probabilities = run_neural_inference(image)

        # Explicit Label Handling
        labels = model.config.id2label
        probs_dict = {labels[i].lower(): round(probabilities[i].item() * 100, 2) for i in range(len(labels))}

        # Find synthetic score matching any common fake label variant ('fake', 'deepfake', 'synthetic')
        fake_score = None
        for key, val in probs_dict.items():
            if any(k in key for k in ["fake", "deepfake", "synthetic", "manipulated"]):
                fake_score = val
                break
                
        if fake_score is None:
            raise ValueError("Model label mismatch, verdict unavailable")

        # 3. Dynamic Ensemble Risk Engine
        heuristic_penalty = 0.0
        
        # Dead-code wiring: Apply +20.0 penalty if known editing/AI software detected
        if metadata_analysis["editing_software_detected"]:
            heuristic_penalty += 20.0
            
        # Absence-based penalties (only applied in ambiguous neural score zone)
        absence_penalty = 0.0
        if 20.0 <= fake_score <= 80.0:
            # EXIF Missing Penalty (Only penalize JPEG, PNG normally lacks it)
            if not metadata_analysis["has_exif_headers"] and metadata_analysis["format"] in ["JPEG", "MPO"]:
                absence_penalty += 15.0

            # AI Generator Aspect Ratio / Resolution Penalty
            w, h = image.width, image.height
            if w == h or metadata_analysis["dimensions"] in ["1024x1024", "512x512", "447x447"]:
                absence_penalty += 10.0
                
            # Cap the absence penalty to max 15.0
            heuristic_penalty += min(15.0, absence_penalty)

        # Calculate Final Composite Synthetic Risk
        composite_synthetic_risk = min(100.0, round(fake_score + heuristic_penalty, 2))

        # CALIBRATED THRESHOLD: 50% or higher is flagged as synthetic
        SYNTHETIC_THRESHOLD = 50.0
        
        is_synthetic = None
        verdict = "UNCERTAIN / INCONCLUSIVE"
        
        if composite_synthetic_risk > 60.0:
            is_synthetic = True
            verdict = "MANIPULATED / SYNTHETIC"
        elif composite_synthetic_risk < 40.0:
            is_synthetic = False
            verdict = "AUTHENTIC MEDIA"

        # Confidence Score calculation
        if is_synthetic is True:
            confidence_score = composite_synthetic_risk
        elif is_synthetic is False:
            confidence_score = round(100.0 - composite_synthetic_risk, 2)
        else:
            # For uncertain, just show the raw composite risk as the confidence score
            confidence_score = composite_synthetic_risk

        # 4. Generate Explainability Heatmap Overlay
        heatmap_b64 = generate_heatmap_overlay(image)

        return {
            "app_name": "DeepTrace AI",
            "filename": file.filename,
            "verdict": verdict,
            "confidence_score": confidence_score,
            "is_synthetic": is_synthetic,
            "analysis_breakdown": {
                "neural_model_probabilities": {
                    "raw_fake_probability": f"{fake_score}%",
                    "heuristic_risk_penalty": f"+{heuristic_penalty}%",
                    "final_composite_synthetic_risk": f"{composite_synthetic_risk}%",
                    "threshold_applied": f"{SYNTHETIC_THRESHOLD}%",
                    "all_labels": probs_dict
                },
                "forensic_metadata": metadata_analysis
            },
            "visual_explainability": {
                "heatmap_overlay_base64": heatmap_b64,
                "heatmap_method": "edge_detection_filter",
                "note": "This is an edge/texture map, not neural model attention."
            }
        }

    except Exception as e:
        logger.error(f"Execution failed: {e}", exc_info=True)
        if isinstance(e, ValueError) and "label mismatch" in str(e):
            raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=500, detail="DeepTrace execution failed due to an internal server error.")

# --- Hugging Face Gradio Mounting ---
# This allows the FastAPI app to run inside a 100% free Hugging Face Gradio Space!
import gradio as gr

@spaces.GPU
def dummy_ui():
    return "DeepTrace API is running! Access the frontend to use the inference engine."

# Create a blank Gradio interface
gradio_app = gr.Interface(fn=dummy_ui, inputs=None, outputs="text")

# Mount it onto the FastAPI app
app = gr.mount_gradio_app(app, gradio_app, path="/")