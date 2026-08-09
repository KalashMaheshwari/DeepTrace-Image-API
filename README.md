# DeepTrace AI

DeepTrace AI is a Multimodal Forensics & Deepfake Detection Platform designed to detect synthetic or manipulated media. It uses a combination of advanced neural models, forensic metadata analysis, and heuristic risk engines to accurately determine if an image or video is authentic or AI-generated.

Currently configured as a modern monorepo running on **Modal** for serverless GPU APIs and **Vercel** for the React frontend.

## Architecture

- **`Image-API/`**: FastAPI service running a SigLIP-based Vision Transformer (`Skullly/DeepFake-image-detection-ViT-384`).
- **`Video-API/`**: FastAPI service running a VideoMAE model (`Vansh180/VideoMae-ffc23-deepfake-detector`).
- **`frontend-react/`**: A stunning, dark-mode-first React dashboard for uploading media and visualizing the forensics reports.

## Features

- **Multimodal Inference**: Supports both Image (JPEG, PNG, WEBP) and Video (MP4, AVI, MOV) analysis.
- **Forensic Metadata Analysis**: Extracts EXIF metadata to identify signatures of known editing software and AI generators.
- **Dynamic Ensemble Risk Engine**: Applies heuristic risk penalties for common AI generation artifacts (missing EXIF, exact square aspect ratios).
- **Visual Explainability**: Generates an edge-enhanced heatmap overlay of the image to highlight manipulated candidate clusters.
- **Serverless GPU Scaling**: Deployed on Modal to ensure instant scale-out with T4 GPUs on demand.

## Deployment to Modal.com

This repository is optimized to be deployed to Modal.

1. Ensure you have a Modal account and have run `modal setup`.
2. To deploy the Image API:
   ```bash
   cd Image-API
   $env:PYTHONIOENCODING="utf-8" # Windows only
   python -m modal deploy modal_deploy.py
   ```
3. To deploy the Video API:
   ```bash
   cd Video-API
   $env:PYTHONIOENCODING="utf-8" # Windows only
   python -m modal deploy modal_deploy.py
   ```

## Frontend Deployment

The frontend can be deployed easily to Vercel or any static host:

1. `cd frontend-react`
2. `npm install`
3. Set your environment variables in Vercel to point to your new Modal API endpoints.
4. `npm run build`
