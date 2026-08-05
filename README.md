# DeepTrace AI

DeepTrace AI is a Multimodal Forensics & Deepfake Detection Platform designed to detect synthetic or manipulated images. It uses a combination of advanced neural models, forensic metadata analysis, and heuristic risk engines to accurately determine if an image is authentic or AI-generated/manipulated.

## Features

- **Neural Inference**: Uses a state-of-the-art SigLIP-based vision model (`prithivMLmods/deepfake-detector-model-v1`) to compute raw deepfake probabilities.
- **Forensic Metadata Analysis**: Extracts EXIF metadata to identify signatures of known editing software and AI generators (e.g., Midjourney, DALL-E, Stable Diffusion, Photoshop).
- **Dynamic Ensemble Risk Engine**: Applies heuristic risk penalties for common AI generation artifacts, such as missing EXIF headers and exact square aspect ratios (e.g., 512x512, 1024x1024).
- **Visual Explainability**: Generates an edge-enhanced heatmap overlay of the image, helping to highlight structural inconsistencies or manipulated candidate clusters.
- **Frontend Dashboard**: A premium, responsive glassmorphic UI for seamless drag-and-drop testing and visual result analysis.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla HTML/CSS/JS (Glassmorphic Dark Theme)
- **Machine Learning**: PyTorch, Transformers (HuggingFace)
- **Image Processing**: Pillow (PIL)

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/KalashMaheshwari/DeepTrace-AI.git
   cd DeepTrace-AI
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn torch transformers pillow python-multipart
   ```

4. **Run the server**:
   ```bash
   uvicorn main:app --reload
   ```

5. **Open the Dashboard**:
   Simply navigate to the `frontend` directory in your file explorer and double-click `index.html` to open it in your browser. (The backend is configured with open CORS, so no dev server is required for the frontend!)

## API Endpoints

### `GET /`
Health check endpoint to verify the system is operational.

### `POST /api/v1/analyze`
Upload an image (`multipart/form-data`) to run the complete forensic pipeline. 

**Response Example:**
```json
{
  "app_name": "DeepTrace AI",
  "filename": "sample.jpg",
  "verdict": "MANIPULATED / SYNTHETIC",
  "confidence_score": 85.4,
  "is_synthetic": true,
  "analysis_breakdown": {
    "neural_model_probabilities": {
      "raw_fake_probability": "70.4%",
      "heuristic_risk_penalty": "+15.0%",
      "final_composite_synthetic_risk": "85.4%",
      "threshold_applied": "30.0%",
      "all_labels": { ... }
    },
    "forensic_metadata": { ... }
  },
  "visual_explainability": {
    "heatmap_overlay_base64": "data:image/jpeg;base64,..."
  }
}
```
