import os
import base64
import io
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/add_timestamp", methods=["POST"])
def add_timestamp():
    try:
        data = request.get_json(force=True)
        if not data or "image" not in data:
            return jsonify({"error": "Missing 'image' in request body"}), 400
        if "timestamp" not in data:
            return jsonify({"error": "Missing 'timestamp' in request body"}), 400

        # decode base64 image
        img_data = base64.b64decode(data["image"])
        image = Image.open(io.BytesIO(img_data)).convert("RGB")
        timestamp = str(data["timestamp"])

        draw = ImageDraw.Draw(image)

        # choose font (try several common paths, fallback to default)
        font_size = int(data.get("font_size", 34))
        font = None
        font_candidates = [
            "arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "DejaVuSans.ttf"
        ]
        for fpath in font_candidates:
            try:
                font = ImageFont.truetype(fpath, font_size)
                break
            except Exception:
                font = None
        if font is None:
            font = ImageFont.load_default()

        # measure text
        try:
            bbox = draw.textbbox((0, 0), timestamp, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except AttributeError:
            text_w, text_h = draw.textsize(timestamp, font=font)

        left_padding = int(data.get("left_padding", 8))
        bottom_padding = int(data.get("bottom_padding", 20))
        x = left_padding
        y = image.height - text_h - bottom_padding

        # draw thin border/shadow for visibility
        border_color = (0, 0, 0)
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(1,-1),(-1,1)]:
            draw.text((x+dx, y+dy), timestamp, font=font, fill=border_color)

        # main text (white)
        draw.text((x, y), timestamp, font=font, fill=(255, 255, 255))

        # output back to base64 jpeg
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return jsonify({"timestamped_image": img_base64})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=True)
