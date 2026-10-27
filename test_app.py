"""Route-level tests that do not download a model or use personal photographs."""
import io
import unittest
from unittest.mock import patch

from PIL import Image
from app import Prediction, create_app


def png_upload():
    buffer = io.BytesIO()
    Image.new("RGB", (96, 96), "white").save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_home_and_assets(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Webcam capture", response.data)
        with self.client.get("/static/app.js") as asset:
            self.assertEqual(asset.status_code, 200)

    def test_reject_missing_and_invalid_images(self):
        self.assertEqual(self.client.post("/analyze").status_code, 400)
        invalid = self.client.post("/analyze?format=json", data={"image": (io.BytesIO(b"invalid"), "a.png")})
        self.assertEqual(invalid.status_code, 400)
        self.assertIn("readable image", invalid.json["error"])

    @patch("app.predict_expressions", return_value=[Prediction("Happy", 0.87, (10, 10, 50, 50))])
    def test_prediction_api_returns_annotation_and_confidence(self, _predict):
        response = self.client.post("/analyze?format=json", data={"image": (png_upload(), "a.png")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["predictions"][0]["emotion"], "Happy")
        self.assertEqual(response.json["predictions"][0]["confidence"], 0.87)
        self.assertTrue(response.json["image_url"].startswith("data:image/png;base64,"))

    @patch("app.predict_expressions", return_value=[])
    def test_no_face_response(self, _predict):
        response = self.client.post("/analyze", data={"image": (png_upload(), "a.png")})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No face was detected", response.data)


if __name__ == "__main__":
    unittest.main()
