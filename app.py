import base64
import io
import re
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont

app = FastAPI(title="Image Timestamp Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Models ----------
class ImageStampRequest(BaseModel):
    base64string: str          # base64 image string
    timestamp: str             # "yyyy-MM-dd HH:mm:ss"
    position: Optional[str] = "bottom-left"
    padding: Optional[int] = 12
    font_ratio: Optional[float] = 0.05
    text_color: Optional[str] = "white"
    outline_color: Optional[str] = "black"
    draw_bg: Optional[bool] = True

# ---------- Helpers ----------
DATA_URL_RX = re.compile(r"^data:image/[^;]+;base64,", re.IGNORECASE)

def _decode_base64_image(s: str) -> Image.Image:
    try:
        if DATA_URL_RX.match(s):
            s = DATA_URL_RX.sub("", s)
        raw = base64.b64decode(s)
        img = Image.open(io.BytesIO(raw))
        return img.convert("RGBA")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image: {e}")

def _load_font(px: int):
    candidates = [
        "fonts/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, px)
        except Exception:
            pass
    return ImageFont.load_default()

def _draw_text_with_outline(draw: ImageDraw.ImageDraw, xy, text, font, fill, outline, stroke=1):
    x, y = xy
    for dx in (-stroke, 0, stroke):
        for dy in (-stroke, 0, stroke):
            if dx or dy:
                draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)

def _text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple:
    try:
        l, t, r, b = draw.textbbox((0, 0), text, font=font)
        return (r - l), (b - t)
    except Exception:
        return draw.textsize(text, font=font)

def _place(position: str, W: int, H: int, w: int, h: int, pad: int) -> tuple:
    pos = position.lower()
    if pos == "bottom-right":
        return W - w - pad, H - h - pad
    if pos == "top-left":
        return pad, pad
    if pos == "top-right":
        return W - w - pad, pad
    if pos == "center":
        return (W - w) // 2, (H - h) // 2
    return pad, H - h - pad

# ---------- Endpoint ----------
@app.post("/write_time")
def write_time(req: ImageStampRequest):
    img = _decode_base64_image(req.base64string)
    W, H = img.size

    font_px = max(12, int(min(W, H) * float(req.font_ratio or 0.05)))
    font = _load_font(font_px)
    draw = ImageDraw.Draw(img, "RGBA")

    text = req.timestamp
    tw, th = _text_size(draw, text, font)
    pad = int(req.padding or 0)
    x, y = _place(req.position or "bottom-left", W, H, tw, th, pad)

    if req.draw_bg:
        rect = (x - 6, y - 4, x + tw + 6, y + th + 4)
        draw.rectangle(rect, fill=(0, 0, 0, 120))

    _draw_text_with_outline(
        draw,
        (x, y),
        text,
        font=font,
        fill=req.text_color or "white",
        outline=req.outline_color or "black",
        stroke=max(1, font_px // 18),
    )

    out = io.BytesIO()
    img.save(out, format="PNG")
    b64 = base64.b64encode(out.getvalue()).decode("ascii")

    return {
        "image": f"data:image/png;base64,{b64}",
        "width": W,
        "height": H,
        "format": "PNG"
    }
