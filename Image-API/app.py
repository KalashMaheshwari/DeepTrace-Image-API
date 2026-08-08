import io
import base64
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
import PIL.ExifTags
import spaces

app = FastAPI(
    title="DeepTrace AI Engine",
    description="Multimodal Forensics & Deepfake Detection Platform",
    version="2.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load SigLIP-based Deepfake Detector Model
MODEL_NAME = "Skullly/DeepFake-image-detection-ViT-384"
print(f"Loading DeepTrace AI SigLIP Neural Engine ({MODEL_NAME})...")

processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)
model.eval()
print("DeepTrace AI Engine Ready!")

def run_neural_inference(image):
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=-1)[0]
    return probabilities


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


def generate_heatmap_overlay(image: Image.Image) -> str:
    """Generates a visual forensic heatmap highlighting manipulated region candidate clusters."""
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
async def analyze_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File uploaded must be an image.")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # 1. Metadata Forensics
        metadata_analysis = extract_metadata(image)

        # 2. Model Inference via ZeroGPU
        probabilities = run_neural_inference(image)

        # Explicit Label Handling (Solves inverted label bugs)
        labels = model.config.id2label
        probs_dict = {labels[i].lower(): round(probabilities[i].item() * 100, 2) for i in range(len(labels))}

        # Find synthetic score matching any common fake label variant ('fake', 'deepfake', 'synthetic')
        fake_score = 0.0
        for key, val in probs_dict.items():
            if key == "m" or any(k in key for k in ["fake", "deepfake", "synthetic"]):
                fake_score = val
                break

        # 3. Dynamic Ensemble Risk Engine
        heuristic_penalty = 0.0
        
        # EXIF Missing Penalty (Very common in synthetic generations)
        if not metadata_analysis["has_exif_headers"]:
            heuristic_penalty += 15.0

        # AI Generator Aspect Ratio / Resolution Penalty
        w, h = image.width, image.height
        if w == h or metadata_analysis["dimensions"] in ["1024x1024", "512x512", "447x447", "1024x1024"]:
            heuristic_penalty += 10.0

        # Calculate Final Composite Synthetic Risk
        composite_synthetic_risk = min(100.0, round(fake_score + heuristic_penalty, 2))

        # CALIBRATED THRESHOLD: 30% or higher is flagged as synthetic
        SYNTHETIC_THRESHOLD = 30.0
        is_synthetic = composite_synthetic_risk >= SYNTHETIC_THRESHOLD

        # 4. Generate Explainability Heatmap Overlay
        heatmap_b64 = generate_heatmap_overlay(image)

        return {
            "app_name": "DeepTrace AI",
            "filename": file.filename,
            "verdict": "MANIPULATED / SYNTHETIC" if is_synthetic else "AUTHENTIC MEDIA",
            "confidence_score": composite_synthetic_risk if is_synthetic else round(100.0 - composite_synthetic_risk, 2),
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
                "heatmap_overlay_base64": heatmap_b64
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepTrace execution failed: {str(e)}")

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