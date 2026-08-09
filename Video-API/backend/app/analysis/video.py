import io
import os
import tempfile

import cv2  # type: ignore
import numpy as np  # type: ignore
import torch

from fastapi import APIRouter, File, UploadFile, HTTPException
from transformers import (
    VideoMAEImageProcessor,
    VideoMAEForVideoClassification,
)
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Video-API")
limiter = Limiter(key_func=get_remote_address)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/v1",
    tags=["Video Analysis"]
)


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "Vansh180/VideoMae-ffc23-deepfake-detector"

processor = None
model = None

def load_models_if_needed():
    global processor, model
    if model is None or processor is None:
        print(f"Loading DeepTrace AI Video Engine ({MODEL_NAME})...")
        processor = VideoMAEImageProcessor.from_pretrained(MODEL_NAME)
        model = VideoMAEForVideoClassification.from_pretrained(MODEL_NAME)
        model.eval()
        
        logger.info(f"Model Labels: {model.config.id2label}")
        expected_keywords = ["fake", "real", "synthetic", "authentic", "manipulated", "deepfake"]
        labels_valid = any(
            any(kw in label.lower() for kw in expected_keywords) 
            for label in model.config.id2label.values()
        )
        if not labels_valid:
            logger.error("Startup Failure: Model labels do not contain expected keywords.")
            raise RuntimeError("Model label validation failed on startup.")
            
        print("DeepTrace AI Video Engine Ready!")


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")



# ============================================================
# VIDEO FRAME EXTRACTION
# ============================================================

def extract_video_frames(
    video_path: str,
    num_frames: int = 16
):
    """
    Extracts uniformly distributed frames from a video.

    The pretrained VideoMAE deepfake detector was trained
    using 16 frames per video clip.
    """

    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        raise ValueError("Unable to open uploaded video.")

    total_frames = int(
        capture.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    fps = capture.get(
        cv2.CAP_PROP_FPS
    )

    width = int(
        capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    duration = (
        total_frames / fps
        if fps and fps > 0
        else 0
    )

    if total_frames <= 0:
        capture.release()
        raise ValueError(
            "Video contains no readable frames."
        )

    # Select 16 frames uniformly across the video
    frame_indices = np.linspace(
        0,
        total_frames - 1,
        num_frames
    ).astype(int)

    frames = []

    for frame_index in frame_indices:

        capture.set(
            cv2.CAP_PROP_POS_FRAMES,
            int(frame_index)
        )

        success, frame = capture.read()

        if not success:
            continue

        # OpenCV BGR -> RGB
        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        frames.append(frame)

    capture.release()

    if len(frames) == 0:
        raise ValueError(
            "Could not extract frames from video."
        )

    # If some frames could not be read,
    # duplicate the last valid frame.
    while len(frames) < num_frames:
        frames.append(frames[-1].copy())

    return (
        frames,
        {
            "total_frames": total_frames,
            "fps": round(float(fps), 2),
            "duration_seconds": round(float(duration), 2),
            "resolution": f"{width}x{height}",
            "frames_analyzed": len(frames),
        }
    )


# ============================================================
# VIDEO MODEL INFERENCE
# ============================================================

def analyze_video_with_model(frames):
    """
    Sends the extracted video frames directly into
    the pretrained VideoMAE deepfake detector.
    """

    # Ensure models are loaded
    load_models_if_needed()
    model.to(DEVICE)

    # Convert frames into model input
    inputs = processor(
        list(frames),
        return_tensors="pt"
    )

    # Move tensors to CPU/GPU
    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }

    with torch.no_grad():

        outputs = model(**inputs)

        logits = outputs.logits

        probabilities = torch.softmax(
            logits,
            dim=-1
        )[0]

    # Model labels
    labels = model.config.id2label

    probabilities_dict = {}

    for index, probability in enumerate(probabilities):

        label = labels.get(
            index,
            str(index)
        )

        probabilities_dict[
            label.lower()
        ] = round(
            probability.item() * 100,
            2
        )

    return probabilities_dict


# ============================================================
# FIND FAKE / REAL SCORES
# ============================================================

def get_fake_probability(probabilities):
    """
    Finds the probability associated with the model's
    fake/deepfake class.
    """

    fake_probability = None
    real_probability = None

    for label, probability in probabilities.items():

        if any(
            keyword in label
            for keyword in [
                "fake",
                "deepfake",
                "synthetic",
                "manipulated"
            ]
        ):
            fake_probability = probability

        if any(
            keyword in label
            for keyword in [
                "real",
                "authentic",
                "original"
            ]
        ):
            real_probability = probability

    if fake_probability is None or real_probability is None:
        raise ValueError("Model label mismatch, verdict unavailable")

    return (
        fake_probability,
        real_probability
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@router.get("/video/health")
def video_health():

    return {
        "system": "DeepTrace AI Video Engine",
        "status": "operational",
        "model": MODEL_NAME,
        "device": str(DEVICE)
    }


# ============================================================
# VIDEO ANALYSIS ENDPOINT
# ============================================================

@router.post("/analyze/video")
@limiter.limit("5/minute")
async def analyze_video(
    request: Request,
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Validate content type
    # --------------------------------------------------------

    allowed_video_types = [
        "video/mp4",
        "video/mpeg",
        "video/quicktime",
        "video/x-msvideo",
        "video/webm",
        "video/x-matroska"
    ]

    if file.content_type not in allowed_video_types:

        raise HTTPException(
            status_code=400,
            detail=(
                "File uploaded must be a supported "
                "video file."
            )
        )

    temp_path = None

    try:

        # ----------------------------------------------------
        # Read uploaded video
        # ----------------------------------------------------

        contents = await file.read()
        
        MAX_FILE_SIZE = 50 * 1024 * 1024
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum size is 50MB."
            )

        if not contents:

            raise HTTPException(
                status_code=400,
                detail="Uploaded video is empty."
            )

        # ----------------------------------------------------
        # Save temporarily
        # ----------------------------------------------------

        suffix = os.path.splitext(
            file.filename or ".mp4"
        )[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            temp_file.write(contents)

            temp_path = temp_file.name

        # ----------------------------------------------------
        # Extract frames
        # ----------------------------------------------------

        frames, video_info = extract_video_frames(
            temp_path,
            num_frames=16
        )

        # ----------------------------------------------------
        # PRETRAINED MODEL
        # ----------------------------------------------------

        probabilities = analyze_video_with_model(
            frames
        )

        # ----------------------------------------------------
        # Get fake/real probabilities
        # ----------------------------------------------------

        fake_probability, real_probability = (
            get_fake_probability(
                probabilities
            )
        )

        # ----------------------------------------------------
        # Determine verdict
        # ----------------------------------------------------

        if fake_probability is None:

            # Generic fallback:
            # choose highest-probability class.

            predicted_label = max(
                probabilities,
                key=probabilities.get
            )

            predicted_probability = probabilities[
                predicted_label
            ]

            is_fake = any(
                keyword in predicted_label
                for keyword in [
                    "fake",
                    "deepfake",
                    "synthetic",
                    "manipulated"
                ]
            )

            confidence = predicted_probability

        else:

            is_fake = (
                fake_probability >
                real_probability
            )

            confidence = (
                fake_probability
                if is_fake
                else real_probability
            )

        # ----------------------------------------------------
        # Final response
        # ----------------------------------------------------

        return {

            "app_name": "DeepTrace AI",

            "filename": file.filename,

            "media_type": "video",

            "verdict": (
                "MANIPULATED / DEEPFAKE"
                if is_fake
                else
                "AUTHENTIC VIDEO"
            ),

            "confidence_score": round(
                confidence,
                2
            ),

            "is_synthetic": is_fake,

            "analysis_breakdown": {

                "pretrained_video_model": {

                    "model_name": MODEL_NAME,

                    "model_type":
                        "VideoMAE Video Classification",

                    "probabilities":
                        probabilities,

                    "fake_probability":
                        fake_probability,

                    "real_probability":
                        real_probability,

                    "frames_analyzed":
                        len(frames)

                },

                "video_information":
                    video_info

            },

            "processing": {

                "device":
                    str(DEVICE),

                "frames_sampled":
                    16,

                "model_based_detection":
                    True

            }

        }

    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Execution failed: {e}", exc_info=True)
        if isinstance(e, ValueError) and "label mismatch" in str(e):
            raise HTTPException(status_code=500, detail=str(e))

        raise HTTPException(
            status_code=500,
            detail="DeepTrace video analysis failed due to an internal server error."
        )

    finally:

        # ----------------------------------------------------
        # Remove temporary video
        # ----------------------------------------------------

        if temp_path and os.path.exists(
            temp_path
        ):

            try:
                os.remove(temp_path)

            except Exception:
                pass