# DeepTrace AI (Image API)

DeepTrace AI is a Multimodal Forensics & Deepfake Detection Platform API designed to detect synthetic or manipulated images. It uses a combination of advanced neural models, forensic metadata analysis, and heuristic risk engines to accurately determine if an image is authentic or AI-generated.

Currently configured to run as a 100% free serverless API on **Hugging Face Spaces** using the Gradio SDK.

## Features

- **Neural Inference**: Uses a state-of-the-art vision model (`Skullly/DeepFake-image-detection-ViT-384`) to compute raw deepfake probabilities.
- **Forensic Metadata Analysis**: Extracts EXIF metadata to identify signatures of known editing software and AI generators.
- **Dynamic Ensemble Risk Engine**: Applies heuristic risk penalties for common AI generation artifacts (missing EXIF, exact square aspect ratios).
- **Visual Explainability**: Generates an edge-enhanced heatmap overlay of the image to highlight manipulated candidate clusters.

## Tech Stack

- **Backend / API**: FastAPI (Python)
- **Deployment**: Hugging Face Spaces (Gradio SDK)
- **Machine Learning**: PyTorch, Transformers (Hugging Face)
- **Image Processing**: Pillow (PIL)

## Deployment to Hugging Face Spaces

This repository is optimized to be deployed as a ZeroGPU Gradio Space on Hugging Face.

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Set a name and choose the **Gradio** Space SDK.
3. Choose the **ZeroGPU** hardware tier (Free).
4. Upload `app.py` and `requirements.txt` to the Files tab of your Space.
5. Hugging Face will automatically install dependencies and launch your API!

## API Usage

Once deployed, your FastAPI application will be accessible via your Hugging Face Space direct API URL. 
*(For example, if your Space is `klshh/DeepTrace-Image-API`, your direct API URL is `https://klshh-deeptrace-image-api.hf.space`)*

### `GET /`
Health check endpoint to verify the system is operational.

### `POST /api/v1/analyze`
Upload an image (`multipart/form-data`) with the key `file` to run the complete forensic pipeline. 

**Response Example:**
```json
{
  "app_name": "DeepTrace AI",
  "filename": "sample.jpg",
  "verdict": "UNCERTAIN / INCONCLUSIVE",
  "confidence_score": 52.4,
  "is_synthetic": null,
  "analysis_breakdown": {
    "neural_model_probabilities": {
      "raw_fake_probability": "52.4%",
      "heuristic_risk_penalty": "+0.0%",
      "final_composite_synthetic_risk": "52.4%",
      "threshold_applied": "50.0%",
      "all_labels": { ... }
    },
    "forensic_metadata": { ... }
  },
  "visual_explainability": {
    "heatmap_overlay_base64": "data:image/jpeg;base64,...",
    "heatmap_method": "edge_detection_filter",
    "note": "This is an edge/texture map, not neural model attention."
  }
}
```
