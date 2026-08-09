from PIL import Image
from pathlib import Path


def analyze_image(file_path: str):
    path = Path(file_path)

    try:
        with Image.open(path) as image:

            has_metadata = False
            # JPEG EXIF
            if hasattr(image, "getexif"):
                raw_exif = image.getexif()
                if raw_exif:
                    has_metadata = True

            # PNG / General Info
            if image.info:
                for key, value in image.info.items():
                    if isinstance(value, (str, bytes)):
                        has_metadata = True

            return {
                "filename": path.name,
                "format": image.format,
                "width": image.width,
                "height": image.height,
                "mode": image.mode,
                "file_size": path.stat().st_size,
                "exif_available": has_metadata,
            }

    except Exception as e:
        return {
            "error": str(e)
        }