from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image


def resize_image(uploaded_file, max_size=400, quality=85, format="JPEG"):
    """
    Resize and compress an uploaded image.
    Returns a new InMemoryUploadedFile with the processed image.
    If the file is an SVG or can't be processed, returns None.
    """
    # Skip non-image formats (SVG, GIF, etc.)
    content_type = getattr(uploaded_file, 'content_type', '') or ''
    name = getattr(uploaded_file, 'name', '') or ''
    if content_type == 'image/svg+xml' or name.lower().endswith('.svg'):
        return None

    try:
        img = Image.open(uploaded_file)
    except Exception:
        return None

    # Convert RGBA/CMYK/P to RGB for JPEG
    original_format = img.format or format
    if img.mode in ('RGBA', 'LA', 'P'):
        rgb = Image.new('RGB', img.size, (255, 255, 255))
        rgb.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = rgb
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Resize if larger than max_size
    if max(img.width, img.height) > max_size:
        ratio = max_size / float(max(img.width, img.height))
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # Save to buffer
    buf = BytesIO()
    save_format = original_format if original_format in ('JPEG', 'PNG', 'WEBP') else 'JPEG'
    img.save(buf, format=save_format, quality=quality, optimize=True)
    buf.seek(0)

    # Determine extension
    ext = save_format.lower()
    if ext == 'jpeg':
        ext = 'jpg'

    new_name = uploaded_file.name.rsplit('.', 1)[0] + '.' + ext if '.' in uploaded_file.name else uploaded_file.name

    return InMemoryUploadedFile(
        buf, None, new_name,
        f'image/{save_format.lower()}',
        buf.tell(), None
    )
