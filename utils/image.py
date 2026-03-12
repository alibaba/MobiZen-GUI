from PIL import Image, ImageDraw
import base64
from io import BytesIO
from typing import Tuple, List, Optional


def resize_image(image_path: str, max_pixels: int, factor: int = 32) -> Tuple[int, int]:
    img = Image.open(image_path)
    width, height = img.size
    
    total_pixels = width * height
    if total_pixels <= max_pixels:
        return width, height
    
    scale = (max_pixels / total_pixels) ** 0.5
    new_width = int(width * scale / factor) * factor
    new_height = int(height * scale / factor) * factor
    
    return new_width, new_height


def image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def image_to_data_url(image_path: str) -> str:
    base64_str = image_to_base64(image_path)
    ext = image_path.split('.')[-1].lower()
    mime_type = f"image/{ext}" if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp'] else "image/png"
    return f"data:{mime_type};base64,{base64_str}"


def draw_circle_on_image(
    image_path: str, 
    coordinates: Tuple[int, int], 
    radius: int = 20, 
    color: str = "red",
    width: int = 3,
    output_path: Optional[str] = None
) -> str:
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    x, y = coordinates
    draw.ellipse(
        [x - radius, y - radius, x + radius, y + radius],
        outline=color,
        width=width
    )
    
    if output_path is None:
        output_path = image_path.replace(".png", "_labeled.png")
    
    img.save(output_path)
    return output_path


def draw_arrow_on_image(
    image_path: str,
    start: Tuple[int, int],
    end: Tuple[int, int],
    color: str = "blue",
    width: int = 3,
    output_path: Optional[str] = None
) -> str:
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    draw.line([start, end], fill=color, width=width)
    
    import math
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    arrow_length = 20
    arrow_angle = math.pi / 6
    
    left_x = end[0] - arrow_length * math.cos(angle - arrow_angle)
    left_y = end[1] - arrow_length * math.sin(angle - arrow_angle)
    right_x = end[0] - arrow_length * math.cos(angle + arrow_angle)
    right_y = end[1] - arrow_length * math.sin(angle + arrow_angle)
    
    draw.line([end, (left_x, left_y)], fill=color, width=width)
    draw.line([end, (right_x, right_y)], fill=color, width=width)
    
    if output_path is None:
        output_path = image_path.replace(".png", "_labeled.png")
    
    img.save(output_path)
    return output_path


def draw_bbox_on_image(
    image_path: str,
    bbox: List[int],
    color: str = "green",
    width: int = 2,
    output_path: Optional[str] = None
) -> str:
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    left, top, right, bottom = bbox
    draw.rectangle([left, top, right, bottom], outline=color, width=width)
    
    if output_path is None:
        output_path = image_path.replace(".png", "_labeled.png")
    
    img.save(output_path)
    return output_path
