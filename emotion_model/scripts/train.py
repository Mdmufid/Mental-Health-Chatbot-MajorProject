"""
Trains DistilBERT on the prepared v3 dataset.
Run after prepare_data.py.
"""

import json
import pandas as pd
import torch
from pathlib import Path
from datasets import Dataset
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score, accuracy_score
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer, TrainingArguments,
    EarlyStoppingCallback
)

# ── Paths ──────────────────────────────────────────
DATA_DIR  = Path("emotion_model/data/processed")
MODEL_OUT = Path("emotion_model/models/transformer_model_v3")
MODEL_OUT.mkdir(parents=True, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# ── Load data ──────────────────────────────────────
train_df = pd.read_csv(DATA_DIR / "train_v3.csv").dropna(subset=["text","label"])
val_df   = pd.read_csv(DATA_DIR / "val_v3.csv").dropna(subset=["text","label"])

# ── Encode labels ──────────────────────────────────
label_encoder = LabelEncoder()
train_df["label_id"] = label_encoder.fit_transform(train_df["label"])
val_df["label_id"]   = label_encoder.transform(val_df["label"])

label_map = {str(k): int(v) for k, v in zip(
    label_encoder.classes_,
    label_encoder.transform(label_encoder.classes_)
)}
with open(MODEL_OUT / "label_map.json", "w") as f:
    json.dump(label_map, f)
print("Label map:", label_map)

# ── Tokenize ───────────────────────────────────────
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

def tokenize(batch):
    return tokenizer(batch["text"], truncation=True,
                     padding="max_length", max_length=128)

train_ds = Dataset.from_pandas(train_df[["text","label_id"]])\
    .rename_column("label_id","labels").map(tokenize, batched=True)
val_ds   = Dataset.from_pandas(val_df[["text","label_id"]])\
    .rename_column("label_id","labels").map(tokenize, batched=True)

train_ds.set_format("torch", columns=["input_ids","attention_mask","labels"])
val_ds.set_format("torch",   columns=["input_ids","attention_mask","labels"])

# ── Model ──────────────────────────────────────────
model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=len(label_encoder.classes_)
)

# ── Train ──────────────────────────────────────────
args = TrainingArguments(
    output_dir=str(MODEL_OUT),
    num_train_epochs=5,
    per_device_train_batch_size=32,
    per_device_eval_batch_size=32,
    warmup_steps=500,
    learning_rate=3e-5,
    weight_decay=0.01,
    logging_dir="emotion_model/logs",
    logging_steps=50,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,
    save_total_limit=2,
    report_to="none",
    fp16=torch.cuda.is_available(),
)

def compute_metrics(pred):
    labels = pred.label_ids
    preds  = pred.predictions.argmax(-1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "f1":       f1_score(labels, preds, average="weighted")
    }

trainer = Trainer(
    model=model, args=args,
    train_dataset=train_ds, eval_dataset=val_ds,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
)

trainer.train()
trainer.save_model(str(MODEL_OUT))
tokenizer.save_pretrained(str(MODEL_OUT))
print(f"\n✅ Model saved to {MODEL_OUT}")