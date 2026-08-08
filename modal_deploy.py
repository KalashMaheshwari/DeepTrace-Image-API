import modal
from fastapi import FastAPI
# Import your existing FastAPI app exactly as it is!
from app import app as fastapi_app

# 1. Define the cloud environment for Modal
# We ask Modal for a Python 3.10 environment and install our requirements
image = modal.Image.debian_slim(python_version="3.10").pip_install(
    "fastapi",
    "uvicorn",
    "torch",
    "torchvision",
    "pillow",
    "python-multipart",
    "transformers",
    "gradio",
    "spaces"
)

# 2. Create a Modal App
app = modal.App("DeepTrace-Image-API", image=image)

# 3. Mount your FastAPI app to a serverless web endpoint!
# We request a free T4 GPU and plenty of memory.
@app.function(gpu="T4")
@modal.asgi_app()
def serve():
    return fastapi_app
