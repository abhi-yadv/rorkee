"""Flask interface for face detection and expression inference.

The app keeps uploaded images only for the current request.  It is a learning
project, not a clinical, safety, or identity-recognition tool.
"""

from __future__ import annotations

import io
import os
from dataclasses import dataclass
from functools import lru_cache
from threading import Lock

import cv2
import numpy as np
from flask import Flask, render_template, request
from PIL import Image

try:
    from fer import FER
except ImportError:  # Allows the UI and explanatory error state to load.
    FER = None


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
INFERENCE_LOCK = Lock()


@dataclass(frozen=True)
class Prediction:
    emotion: str
    confidence: float
    box: tuple[int, int, int, int]


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def decode_image(payload: bytes) -> np.ndarray:
    """Decode a supported image while rejecting malformed uploads."""
    if not payload or len(payload) > MAX_UPLOAD_BYTES:
        raise ValueError("Upload a valid image smaller than 5 MB.")
    try:
        image = Image.open(io.BytesIO(payload)).convert("RGB")
    except Exception as exc:
        raise ValueError("The uploaded file is not a readable image.") from exc
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


@lru_cache(maxsize=1)
def get_detector():
    if FER is None:
        raise RuntimeError("The FER dependency is unavailable. Run pip install -r requirements.txt.")
    return FER(mtcnn=False)


def predict_expressions(image: np.ndarray) -> list[Prediction]:
    """Run the FER package's bundled CNN inference and return sorted results."""
    with INFERENCE_LOCK:
        results = get_detector().detect_emotions(image)
    predictions: list[Prediction] = []
    for result in results:
        scores = result.get("emotions", {})
        if not scores:
            continue
        emotion, confidence = max(scores.items(), key=lambda item: item[1])
        x, y, width, height = result["box"]
        predictions.append(Prediction(emotion.title(), float(confidence), (x, y, width, height)))
    return sorted(predictions, key=lambda item: item.confidence, reverse=True)


def annotate(image: np.ndarray, predictions: list[Prediction]) -> Image.Image:
    canvas = image.copy()
    for prediction in predictions:
        x, y, width, height = prediction.box
        cv2.rectangle(canvas, (x, y), (x + width, y + height), (30, 144, 255), 2)
        label = f"{prediction.emotion} {prediction.confidence:.0%}"
        cv2.putText(canvas, label, (x, max(y - 8, 18)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (30, 144, 255), 2)
    return Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))


def image_data_url(image: Image.Image) -> str:
    import base64

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/analyze")
    def analyze():
        wants_json = request.args.get("format") == "json"

        def error_response(message, status=400):
            if wants_json:
                return {"error": message}, status
            return render_template("index.html", error=message), status

        uploaded = request.files.get("image")
        if uploaded is None or not uploaded.filename:
            return error_response("Choose a JPG, PNG, or WEBP image first.")
        if not allowed_file(uploaded.filename):
            return error_response("Use JPG, PNG, or WEBP only.")
        try:
            image = decode_image(uploaded.read())
            predictions = predict_expressions(image)
        except (ValueError, RuntimeError) as exc:
            return error_response(str(exc))
        except Exception:
            app.logger.exception("Expression inference failed")
            return error_response("Inference could not complete for this image.", 500)

        if wants_json:
            return {
                "predictions": [{"emotion": p.emotion, "confidence": p.confidence} for p in predictions],
                "image_url": image_data_url(annotate(image, predictions)),
                "no_face": not predictions,
            }

        return render_template(
            "index.html",
            predictions=predictions,
            image_url=image_data_url(annotate(image, predictions)),
            no_face=not predictions,
        )

    @app.errorhandler(413)
    def file_too_large(_error):
        return render_template("index.html", error="The image must be smaller than 5 MB."), 413

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")))
