import base64
import fitz
from io import BytesIO
from PIL import Image


def pdf_to_base64_images(pdf_path, dpi=200):
    doc = fitz.open(pdf_path)
    base64_images = []

    for page in doc:
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)

        pix = page.get_pixmap(matrix=mat)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=80)
        buffer.seek(0)

        encoded = base64.b64encode(buffer.read()).decode("utf-8")
        base64_images.append(encoded)

    return base64_images
