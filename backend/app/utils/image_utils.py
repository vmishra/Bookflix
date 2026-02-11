"""Image processing utilities."""
from PIL import Image
import io


def resize_cover(image_data: bytes, max_width: int = 400, max_height: int = 600) -> bytes:
    img = Image.open(io.BytesIO(image_data))
    img.thumbnail((max_width, max_height), Image.LANCZOS)
    output = io.BytesIO()
    img.save(output, format="PNG", optimize=True)
    return output.getvalue()


def generate_placeholder_cover(title: str, author: str = "") -> bytes:
    """Generate a simple colored placeholder cover."""
    img = Image.new("RGB", (400, 600), color=_title_to_color(title))
    output = io.BytesIO()
    img.save(output, format="PNG")
    return output.getvalue()


def _title_to_color(title: str) -> tuple:
    h = hash(title) % 360
    # Simple HSL to RGB (approximation)
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(h / 360.0, 0.4, 0.7)
    return (int(r * 255), int(g * 255), int(b * 255))
