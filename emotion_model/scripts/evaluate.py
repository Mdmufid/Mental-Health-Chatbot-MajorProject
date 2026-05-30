"""
Evaluates a trained model and prints full classification report.
"""

import json
import pandas as pd
from pathlib import Path
from datasets import Dataset
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments
import os

MODEL_PATH = Path("emotion_model/models/transformer_model_v3")
VAL_PATH   = Path("emotion_model/data/processed/val_v3.csv")

val_df = pd.read_csv(VAL_PATH).dropna(subset=["text","label"])
val_df = val_df[val_df["text"].str.strip() != ""]

label_encoder = LabelEncoder()
val_df["labels"] = label_encoder.fit_transform(val_df["label"])
class_names = label_encoder.classes_

tokenizer = DistilBertTokenizerFast.from_pretrained(str(MODEL_PATH))
model     = DistilBertForSequenceClassification.from_pretrained(str(MODEL_PATH))

def tokenize(batch):
    return tokenizer(batch["text"], truncation=True, padding="max_length", max_length=128)

val_ds = Dataset.from_pandas(val_df[["text","labels"]])\
    .map(tokenize, batched=True)
val_ds.set_format("torch", columns=["input_ids","attention_mask","labels"])

os.makedirs("./temp_eval", exist_ok=True)
args = TrainingArguments(output_dir="./temp_eval", report_to="none",
                         per_device_eval_batch_size=32)
trainer = Trainer(model=model, args=args, eval_dataset=val_ds)

output = trainer.predict(val_ds)
preds  = output.predictions.argmax(-1)
labels = output.label_ids

print("\n" + "="*40)
print("MODEL PERFORMANCE METRICS")
print("="*40)
print(f"Accuracy : {accuracy_score(labels, preds):.4f}")
print(f"F1-Score : {f1_score(labels, preds, average='weighted'):.4f}")
print("\nPER-CLASS REPORT:")
print(classification_report(labels, preds, target_names=class_names))