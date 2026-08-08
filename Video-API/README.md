# Deeptrace-Video-API

# 🎥 DeepTrace AI — Video Deepfake Detection

> **AI-powered video authenticity analysis using frame sampling and deepfake detection models.**

DeepTrace AI is a multimodal media forensics system. This repository section focuses specifically on its **video deepfake detection pipeline**, designed to analyze uploaded videos and determine whether they are likely to be **REAL** or **MANIPULATED / AI-GENERATED**.

---

## 🚀 Features

* 🎥 Upload and analyze video files
* 🔍 Automatic video validation
* 🧩 Frame/clip sampling from uploaded videos
* 🤖 Pretrained AI model-based analysis
* 📊 Aggregation of predictions across sampled frames/clips
* 🎯 Authenticity confidence score
* ⚠️ Classification as:

  * **REAL**
  * **MANIPULATED**
* ⚡ FastAPI-based backend
* 📚 Interactive API documentation through Swagger UI

---

## 🧠 How It Works

The video detection pipeline follows these steps:

```text
              Upload Video
                   │
                   ▼
           Video Validation
                   │
                   ▼
          Frame / Clip Sampling
                   │
                   ▼
        Pretrained AI Model
                   │
                   ▼
        Frame/Clip Predictions
                   │
                   ▼
         Score Aggregation
                   │
                   ▼
       ┌─────────────────────┐
       │   Final Analysis    │
       └─────────────────────┘
             │           │
             ▼           ▼
           REAL      MANIPULATED
             │           │
             └─────┬─────┘
                   ▼
          Confidence Score
```

### 1. Video Upload

The user submits a video through the API.

The backend accepts the uploaded file and temporarily stores it for processing.

### 2. Video Validation

Before analysis, the uploaded file is validated to ensure that:

* The file is a supported video format.
* The video can be opened successfully.
* Frames can be extracted correctly.

### 3. Frame / Clip Sampling

Instead of processing every frame of a long video, DeepTrace samples selected frames or clips.

This reduces computational requirements while still providing representative information about the video.

Example:

```text
Video
 │
 ├── Frame 1
 ├── Frame 30
 ├── Frame 60
 ├── Frame 90
 ├── Frame 120
 └── ...
```

### 4. AI-Based Detection

The sampled frames/clips are passed through a pretrained deepfake detection model.

The model generates predictions for the sampled content.

```text
Sample 1 → Model → Prediction
Sample 2 → Model → Prediction
Sample 3 → Model → Prediction
       ...
```

### 5. Prediction Aggregation

Individual predictions are combined to produce an overall video-level result.

This prevents the final decision from depending on a single frame.

```text
Frame Predictions
       │
       ▼
 ┌───────────────┐
 │ Aggregation   │
 │    Engine     │
 └───────────────┘
       │
       ▼
Video-Level Score
```

### 6. Final Result

The system returns a final classification along with a confidence score.

Example:

```json
{
  "result": "MANIPULATED",
  "confidence": 94.7
}
```

---

## 🛠️ Technology Stack

| Technology                | Purpose                      |
| ------------------------- | ---------------------------- |
| Python                    | Core development             |
| FastAPI                   | Backend API                  |
| Uvicorn                   | ASGI server                  |
| PyTorch                   | Deep learning inference      |
| Hugging Face Transformers | Pretrained model integration |
| OpenCV / Video Processing | Frame extraction             |
| FFmpeg                    | Video processing support     |

---

## 📁 Project Structure

```text
DeepTrace/
│
├── app/
│   ├── main.py
│   ├── routers/
│   │   └── video.py
│   │
│   ├── services/
│   │   └── video_detector.py
│   │
│   └── models/
│       └── video_model.py
│
├── videos/
│   └── .gitkeep
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

> The exact structure may vary depending on the implementation and model being used.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/DeepTrace.git
cd DeepTrace
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**macOS / Linux**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the FastAPI server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## 📖 API Documentation

DeepTrace uses FastAPI's automatically generated API documentation.

After starting the server, open:

```text
http://127.0.0.1:8000/docs
```

You can use Swagger UI to:

1. Select the video detection endpoint.
2. Upload a video.
3. Execute the request.
4. View the detection result and confidence score.

---

## 🎬 Supported Video Formats

The API can be configured to support common formats such as:

```text
.mp4
.avi
.mov
.mkv
.webm
```

The exact supported extensions depend on the validation configuration.

---

## 📊 Example Detection Flow

### Input

```text
uploaded_video.mp4
```

### Processing

```text
Video
  ↓
Validation
  ↓
Frame Sampling
  ↓
AI Model
  ↓
Individual Predictions
  ↓
Score Aggregation
```

### Output

```json
{
  "filename": "uploaded_video.mp4",
  "result": "REAL",
  "confidence": 91.3
}
```

or

```json
{
  "filename": "uploaded_video.mp4",
  "result": "MANIPULATED",
  "confidence": 96.8
}
```

---

## 🔬 Why Multiple Frames?

A deepfake may not exhibit obvious artifacts throughout the entire video.

Some frames may appear completely normal while other frames contain:

* Facial inconsistencies
* Temporal artifacts
* Unnatural expressions
* Blending errors
* Identity inconsistencies
* AI-generated visual patterns

Therefore, analyzing multiple samples provides a more reliable video-level assessment than analyzing a single frame.

---

## ⚠️ Important Note

DeepTrace's result represents an **AI-based forensic assessment**, not an absolute determination of authenticity.

A high confidence score indicates that the model strongly favors a particular classification, but it should not be treated as definitive proof.

Performance can vary depending on:

* Video quality
* Compression
* Resolution
* Lighting
* Face visibility
* Video length
* Type of manipulation
* Generation/manipulation technique
* Model limitations

---

## 🔮 Future Improvements

Planned improvements for the video detection pipeline include:

* [ ] Temporal deepfake detection
* [ ] Video transformer models
* [ ] Face-specific analysis
* [ ] Audio-video consistency analysis
* [ ] Lip-sync detection
* [ ] Multiple model ensemble
* [ ] Explainable detection results
* [ ] Heatmaps / suspicious-frame visualization
* [ ] Advanced temporal artifact analysis
* [ ] GPU acceleration
* [ ] Batch video analysis

---

## 🎯 Project Goal

The goal of DeepTrace is to provide a practical **digital media forensics pipeline** capable of helping users identify potentially manipulated and AI-generated media.

The video component focuses on moving beyond single-image classification by analyzing **multiple temporal samples from an entire video**.

---

## ⚖️ Disclaimer

DeepTrace is intended for **research, educational, and digital-media-forensics purposes**.

AI-based deepfake detection is an evolving field, and no detection system can guarantee 100% accuracy for every type of manipulated or AI-generated video.

---

## 👩‍💻 Development

Built as part of the **DeepTrace AI Engine** project.

**Focus:** Video Deepfake Detection
**Backend:** FastAPI
**Language:** Python
**Domain:** AI / Machine Learning / Digital Forensics
