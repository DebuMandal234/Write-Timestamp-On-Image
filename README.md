# Image Timestamp Service (FastAPI)

Small service that accepts a base64 image and a timestamp, draws the timestamp onto the image and returns the updated image as a base64 data-URL.

## Files
- `app.py` - FastAPI application (POST /stamp).
- `requirements.txt` - Python dependencies.
- `fonts/DejaVuSans.ttf` - Optional local font to ensure consistent text rendering.
- `.gitignore` - recommended ignores.

---

## Quick features
- Accepts `image` (base64 string or data URL) and `timestamp` string.
- Positioning: `bottom-left`, `bottom-right`, `top-left`, `top-right`, `center`.
- Optional background box behind text and outline for readability.

---

## Prerequisites (local)
- Python 3.9+ (3.11 tested)
- Git
- (Optional) Render account for deployment

---

## Local setup & test

1. Clone the repo (or create from files):
```bash
git clone https://github.com/<your-username>/<repo>.git
cd <repo>
