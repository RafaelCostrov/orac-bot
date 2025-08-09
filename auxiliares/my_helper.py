import base64
from pdf2image import convert_from_path
from io import BytesIO


def pdf_to_base64_images(pdf_path, dpi=200):
    poppler_path = r"C:\Users\rafae\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"
    pages = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)

    base64_images = []
    for image in pages:
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        buffer.seek(0)
        encoded = base64.b64encode(buffer.read()).decode('utf-8')
        base64_images.append(encoded)
    return base64_images
