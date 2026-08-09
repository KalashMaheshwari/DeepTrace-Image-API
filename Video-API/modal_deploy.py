import modal
import sys
import os

# Add the backend directory to sys.path so the local Modal client 
# can find the 'app' module when inspecting the AST for auto-mounting.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# 1. Define the cloud environment for Modal
# We ask Modal for a Python 3.10 environment and install our requirements
image = (
    modal.Image.debian_slim(python_version="3.10")
    # Install dependencies
    .pip_install(
        "fastapi",
        "uvicorn",
        "torch",
        "torchvision",
        "transformers",
        "opencv-python-headless",
        "python-multipart",
        "slowapi"
    )
    # Bake the model into the container during the build phase to avoid cold starts!
    .run_commands(
        "python -c 'from transformers import VideoMAEImageProcessor, VideoMAEForVideoClassification; "
        "VideoMAEImageProcessor.from_pretrained(\"Vansh180/VideoMae-ffc23-deepfake-detector\"); "
        "VideoMAEForVideoClassification.from_pretrained(\"Vansh180/VideoMae-ffc23-deepfake-detector\")'"
    )
    # Add our local backend app folder and all its files to the cloud
    .add_local_dir("backend/app", remote_path="/root/app")
)

# 2. Create a Modal App
app = modal.App("DeepTrace-Video-API", image=image)

# 3. Mount your FastAPI app to a serverless web endpoint!
# We request a free T4 GPU and plenty of memory.
@app.function(gpu="T4")
@modal.asgi_app()
def serve():
    # Import inside the function so Modal mounts it into the cloud!
    import importlib
    app_main = importlib.import_module("app.main")
    return app_main.app
