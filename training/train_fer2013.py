"""Train a small FER-2013 CNN from local, licensed data.

Expected layout: data/fer2013/{train,validation,test}/{angry,disgust,fear,happy,
neutral,sad,surprise}/*.png.  The dataset itself is deliberately not stored in
this repository; review its license before use.
"""
from pathlib import Path
import tensorflow as tf

DATA_DIR = Path("data/fer2013")
IMAGE_SIZE = (48, 48)
BATCH_SIZE = 64
EPOCHS = 20
CLASS_NAMES = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]

def load_split(name: str, shuffle: bool):
    return tf.keras.utils.image_dataset_from_directory(
        DATA_DIR / name, color_mode="grayscale", image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE, label_mode="categorical", shuffle=shuffle,
        class_names=CLASS_NAMES, seed=42,
    )

def main():
    tf.keras.utils.set_random_seed(42)
    train = load_split("train", True).map(lambda x, y: (x / 255.0, y)).prefetch(tf.data.AUTOTUNE)
    validation = load_split("validation", False).map(lambda x, y: (x / 255.0, y)).prefetch(tf.data.AUTOTUNE)
    test = load_split("test", False).map(lambda x, y: (x / 255.0, y)).prefetch(tf.data.AUTOTUNE)
    model = tf.keras.Sequential([
        tf.keras.layers.Input((*IMAGE_SIZE, 1)),
        tf.keras.layers.Conv2D(32, 3, activation="relu"), tf.keras.layers.MaxPool2D(),
        tf.keras.layers.Conv2D(64, 3, activation="relu"), tf.keras.layers.MaxPool2D(),
        tf.keras.layers.Dropout(0.25), tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation="relu"), tf.keras.layers.Dropout(0.4),
        tf.keras.layers.Dense(7, activation="softmax"),
    ])
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    model.fit(train, validation_data=validation, epochs=EPOCHS,
              callbacks=[tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True)])
    Path("models").mkdir(exist_ok=True)
    model.save("models/fer2013_cnn.keras")
    import json
    metrics = model.evaluate(test, return_dict=True)
    Path("models/class_names.json").write_text(json.dumps(CLASS_NAMES), encoding="utf-8")
    Path("models/test_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
