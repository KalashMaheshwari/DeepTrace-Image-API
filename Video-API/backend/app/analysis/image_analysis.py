from PIL import Image
from pathlib import Path


def analyze_image(file_path: str):
    path = Path(file_path)

    try:
        with Image.open(path) as image:

            return {
                "filename": path.name,
                "format": image.format,
                "width": image.width,
                "height": image.height,
                "mode": image.mode,
                "file_size": path.stat().st_size,
                "exif_available": bool(image.getexif()),
            }

    except Exception as e:
        return {
            "error": str(e)
        }