"""
Train a CNN model using PlantVillage-style directory datasets.

Expected structure:
dataset/
  train/
    ClassA/
    ClassB/
  validation/
    ClassA/
    ClassB/
"""

import argparse
import json
from pathlib import Path

import tensorflow as tf


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-dir", required=True)
    parser.add_argument("--val-dir", required=True)
    parser.add_argument("--output-model", default="backend/models/crop_disease_cnn.h5")
    parser.add_argument("--output-labels", default="backend/models/labels.json")
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=8)
    return parser.parse_args()


def build_model(num_classes: int, image_size: int):
    base = tf.keras.applications.MobileNetV2(
        input_shape=(image_size, image_size, 3),
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False

    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(image_size, image_size, 3)),
            tf.keras.layers.Rescaling(1.0 / 255),
            base,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(num_classes, activation="softmax"),
        ]
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def main():
    args = parse_args()

    image_size_tuple = (args.image_size, args.image_size)
    train_ds = tf.keras.utils.image_dataset_from_directory(
        args.train_dir,
        image_size=image_size_tuple,
        batch_size=args.batch_size,
        label_mode="int",
        shuffle=True,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        args.val_dir,
        image_size=image_size_tuple,
        batch_size=args.batch_size,
        label_mode="int",
        shuffle=False,
    )

    class_names = train_ds.class_names
    num_classes = len(class_names)
    print(f"Detected {num_classes} classes")

    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(autotune)
    val_ds = val_ds.prefetch(autotune)

    model = build_model(num_classes=num_classes, image_size=args.image_size)
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=3,
            restore_best_weights=True,
        )
    ]
    model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=callbacks)

    output_model = Path(args.output_model)
    output_labels = Path(args.output_labels)
    output_model.parent.mkdir(parents=True, exist_ok=True)
    output_labels.parent.mkdir(parents=True, exist_ok=True)

    model.save(output_model)
    with output_labels.open("w", encoding="utf-8") as fp:
        json.dump(class_names, fp, indent=2)

    print(f"Saved model to {output_model}")
    print(f"Saved labels to {output_labels}")


if __name__ == "__main__":
    main()
