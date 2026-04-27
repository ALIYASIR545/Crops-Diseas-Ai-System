"""
Train crop disease model directly from Kaggle PlantVillage directory.

This script:
- Reads class folders from a single data root
- Ignores empty folders
- Builds train/validation split with stratification
- Trains a transfer-learning CNN
- Saves model + labels + training summary JSON
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import List, Tuple

import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True, help="Path to PlantVillage class folders")
    parser.add_argument("--output-model", default="backend/models/crop_disease_cnn.h5")
    parser.add_argument("--output-labels", default="backend/models/labels.json")
    parser.add_argument("--output-summary", default="backend/models/training_summary.json")
    parser.add_argument(
        "--dataset-source",
        default="custom dataset",
        help="Human-readable source description saved into training summary",
    )
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--fine-tune-epochs", type=int, default=1)
    parser.add_argument("--fine-tune-layers", type=int, default=30)
    parser.add_argument("--val-split", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def collect_paths_and_labels(data_dir: Path) -> Tuple[List[str], List[int], List[str], dict]:
    class_dirs = [d for d in sorted(data_dir.iterdir()) if d.is_dir()]
    class_names = []
    class_counts = {}
    image_paths = []
    labels = []

    for class_dir in class_dirs:
        # Ignore accidental nested mirror folder (e.g., PlantVillage/PlantVillage/...).
        if class_dir.name.lower() == data_dir.name.lower():
            continue

        files = [p for p in class_dir.iterdir() if p.is_file() and p.suffix.lower() in VALID_EXTENSIONS]
        if not files:
            continue

        label_index = len(class_names)
        class_names.append(class_dir.name)
        class_counts[class_dir.name] = len(files)
        for fp in files:
            image_paths.append(str(fp))
            labels.append(label_index)

    return image_paths, labels, class_names, class_counts


def decode_and_resize(path: tf.Tensor, label: tf.Tensor, image_size: int):
    image_bytes = tf.io.read_file(path)
    image = tf.io.decode_image(image_bytes, channels=3, expand_animations=False)
    image = tf.image.resize(image, [image_size, image_size])
    image = tf.cast(image, tf.float32) / 255.0
    return image, label


def make_dataset(paths: List[str], labels: List[int], image_size: int, batch_size: int, training: bool):
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    if training:
        ds = ds.shuffle(buffer_size=min(len(paths), 10000), reshuffle_each_iteration=True)
    ds = ds.map(lambda x, y: decode_and_resize(x, y, image_size), num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return ds


def build_model(num_classes: int, image_size: int):
    try:
        backbone = tf.keras.applications.MobileNetV2(
            input_shape=(image_size, image_size, 3),
            include_top=False,
            weights="imagenet",
        )
    except Exception:
        backbone = tf.keras.applications.MobileNetV2(
            input_shape=(image_size, image_size, 3),
            include_top=False,
            weights=None,
        )

    backbone.trainable = False

    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(image_size, image_size, 3)),
            backbone,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dropout(0.25),
            tf.keras.layers.Dense(num_classes, activation="softmax"),
        ]
    )
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model, backbone


def main():
    args = parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    tf.random.set_seed(args.seed)

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    image_paths, labels, class_names, class_counts = collect_paths_and_labels(data_dir)
    if not image_paths:
        raise RuntimeError("No image files found in data directory.")

    train_paths, val_paths, train_labels, val_labels = train_test_split(
        image_paths,
        labels,
        test_size=args.val_split,
        random_state=args.seed,
        stratify=labels,
    )

    train_ds = make_dataset(train_paths, train_labels, args.image_size, args.batch_size, training=True)
    val_ds = make_dataset(val_paths, val_labels, args.image_size, args.batch_size, training=False)

    model, backbone = build_model(num_classes=len(class_names), image_size=args.image_size)
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=2,
            restore_best_weights=True,
        )
    ]
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=callbacks,
    )

    if args.fine_tune_epochs > 0:
        backbone.trainable = True
        if args.fine_tune_layers > 0:
            for layer in backbone.layers[:-args.fine_tune_layers]:
                layer.trainable = False
        for layer in backbone.layers:
            # Keep batch norm layers frozen for stable fine-tuning.
            if isinstance(layer, tf.keras.layers.BatchNormalization):
                layer.trainable = False

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )
        fine_history = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=args.fine_tune_epochs,
            callbacks=callbacks,
        )
        for key, values in fine_history.history.items():
            history.history.setdefault(key, []).extend(values)

    output_model = Path(args.output_model)
    output_labels = Path(args.output_labels)
    output_summary = Path(args.output_summary)
    output_model.parent.mkdir(parents=True, exist_ok=True)
    output_labels.parent.mkdir(parents=True, exist_ok=True)
    output_summary.parent.mkdir(parents=True, exist_ok=True)

    model.save(output_model)
    with output_labels.open("w", encoding="utf-8") as fp:
        json.dump(class_names, fp, indent=2)

    summary = {
        "dataset_source": args.dataset_source,
        "data_dir": str(data_dir),
        "total_images": len(image_paths),
        "class_count": len(class_names),
        "class_counts": class_counts,
        "train_size": len(train_paths),
        "val_size": len(val_paths),
        "epochs_requested": args.epochs,
        "fine_tune_epochs": args.fine_tune_epochs,
        "best_val_accuracy": float(max(history.history.get("val_accuracy", [0.0]))),
        "final_train_accuracy": float(history.history.get("accuracy", [0.0])[-1]),
        "final_val_accuracy": float(history.history.get("val_accuracy", [0.0])[-1]),
        "class_names": class_names,
    }
    with output_summary.open("w", encoding="utf-8") as fp:
        json.dump(summary, fp, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"Saved model to: {output_model}")
    print(f"Saved labels to: {output_labels}")
    print(f"Saved summary to: {output_summary}")


if __name__ == "__main__":
    main()
