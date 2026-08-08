# DeepTrace AI

DeepTrace AI is a Multimodal Forensics & Deepfake Detection Platform built by **Team Nexus**. It is designed to detect synthetic or manipulated images using a combination of advanced neural models, forensic metadata analysis, and heuristic risk engines.

## Features

- **AIDE Neural Inference**: Powered by the cutting-edge AIDE (ICLR 2025) dual-branch neural network, analyzing both DCT+SRM noise features and CLIP semantic embeddings.
- **Forensic Metadata Analysis**: Extracts EXIF metadata to identify signatures of known editing software and AI generators (e.g., Midjourney, DALL-E, Stable Diffusion, Photoshop).
- **Dynamic Ensemble Risk Engine**: Applies heuristic risk penalties for common AI generation artifacts, such as missing EXIF headers and exact square aspect ratios.
- **Premium User-Friendly Dashboard**: A sophisticated, Claude-inspired React dashboard featuring soft typography, earthy themes, and plain-English explanations of forensic results for non-technical users.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React (Vite) + Minimalist Vanilla CSS
- **Machine Learning**: PyTorch, AIDE (ICLR 2025 Architecture)
- **Image Processing**: Pillow (PIL), Torchvision

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/KalashMaheshwari/DeepTrace-AI.git
   cd DeepTrace-AI
   ```

2. **Backend Setup (Python)**:
   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Mac/Linux: source venv/bin/activate
   pip install -r requirements.txt
   ```
   *Note: Ensure you have cloned the AIDE repository and downloaded the checkpoint into the `weights/` folder as per the AIDE documentation.*

3. **Run the Backend Server**:
   ```bash
   uvicorn main:app --reload
   ```

4. **Frontend Setup (React)**:
   Open a new terminal window:
   ```bash
   cd dashboard
   npm install
   npm run dev
   ```
   Navigate to the provided localhost link (usually `http://localhost:5173`) to use the application.

## API Endpoints

### `GET /`
Health check endpoint to verify the system is operational.

### `POST /api/v1/analyze`
Upload an image (`multipart/form-data`) to run the complete forensic pipeline. 

**Response Example:**
```json
{
  "app_name": "DeepTrace AI Premium",
  "filename": "sample.jpg",
  "verdict": "MANIPULATED / SYNTHETIC",
  "confidence_score": 85.4,
  "is_synthetic": true,
  "analysis_breakdown": {
    "neural_model_probabilities": {
      "aide_raw_fake_probability": "70.4%",
      "heuristic_risk_penalty": "+15.0%",
      "final_composite_synthetic_risk": "85.4%",
      "threshold_applied": "30.0%"
    },
    "forensic_metadata": { ... }
  }
}
```
