# Facial Expression Recognition

A portfolio project that detects visible faces in an uploaded image and estimates an expression label with the [`fer`](https://pypi.org/project/fer/) package's pre-trained CNN. The UI is built with Flask; face boxes and predicted labels are drawn with OpenCV.

> **Scope and limitations:** This is an experimental educational project, not an emotion-reading system. A model output is not a fact about a person's feelings. Do not use it for healthcare, hiring, education, law enforcement, identity, safety, or other high-impact decisions.

## Features

- Validates JPG, PNG and WEBP uploads (maximum 5 MB)
- Detects each visible face and shows the top predicted label plus confidence
- Keeps images in memory for the current request; it does not save uploads
- Browser webcam start/stop and explicit frame capture for analysis
- Last 10 predictions kept in tab session storage, with no images saved
- Includes a separate, local FER-2013 CNN training script

## Run locally

Use Python 3.11 or 3.12. Initial installation downloads TensorFlow and FER's dependencies and can take several minutes.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Training workflow

`training/train_fer2013.py` expects a locally obtained, appropriately licensed FER-2013-style folder layout described in its module docstring. It does not download or commit a dataset. With the dependencies installed, run:

```bash
python training/train_fer2013.py
```

Use separate `train`, `validation` and `test` folders. Early stopping uses validation only; the test split is evaluated once after training. The script saves the label order and measured test metrics alongside the model. No training accuracy is claimed in this repository.

The training workflow is separate from the web demo. Its saved model is not automatically used by the `fer` package; integrating a custom model should include held-out evaluation, per-class metrics and documented preprocessing.

Webcam capture requires localhost or HTTPS and explicit browser permission. Run this app locally; the previous Vercel carbon-dashboard deployment does not serve this Python application.

## Attribution

Inference uses [Justin Shenk's FER package](https://github.com/justinshenk/fer) and its bundled pre-trained model. This application adds a Flask interface, upload validation, image annotations and browser webcam capture; it does not claim authorship of the pre-trained model.

## Repository hygiene

Do not commit datasets, trained weights, personal images, API keys, or `.env` files. Record dataset licenses and report accuracy only after a reproducible held-out evaluation.

## Tech

Python, Flask, OpenCV, Pillow, NumPy, FER and TensorFlow
