import os
import pandas as pd
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from pathlib import Path
import json
import numpy as np
import pandas as pd

# 1. Setup Paths (Same as your training script)
model_path = Path("emotion_model/models/transformer_model_v2")
val_path = Path("data/processed/val.csv")

# 2. Load Validation Data
val_df = pd.read_csv(val_path).dropna(subset=["text", "label"])
val_df = val_df[val_df["text"].str.strip() != ""]

# 3. Encode Labels (Ensure this matches your training logic)
label_encoder = LabelEncoder()
# We fit on the labels to ensure the ID mapping is consistent
val_df["labels"] = label_encoder.fit_transform(val_df["label"])

# 4. Load Saved Model and Tokenizer
tokenizer = DistilBertTokenizerFast.from_pretrained(str(model_path))
model = DistilBertForSequenceClassification.from_pretrained(str(model_path))

# 5. Tokenize Data
def tokenize(batch):
    return tokenizer(batch["text"], truncation=True, padding="max_length", max_length=128)

val_ds = Dataset.from_pandas(val_df[["text", "labels"]])
val_ds = val_ds.map(tokenize, batched=True)
val_ds.set_format("torch", columns=["input_ids", "attention_mask", "labels"])

# 6. Define Metrics Function
def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    acc = accuracy_score(labels, preds)
    f1 = f1_score(labels, preds, average='weighted')
    return {"accuracy": acc, "f1": f1}

# Create the temp directory if it doesn't exist to prevent errors
if not os.path.exists("./temp_eval"):
    os.makedirs("./temp_eval")

# 7. Initialize Trainer just for evaluation
args = TrainingArguments(
    output_dir="./temp_eval",
    report_to="none",
    per_device_eval_batch_size=8
)
trainer = Trainer(
    model=model,
    args=args,
    eval_dataset=val_ds,
    compute_metrics=compute_metrics
)

# 8. Run Evaluation
print("📊 Evaluating model... please wait.")
metrics = trainer.evaluate()

# Get raw predictions
preds_output = trainer.predict(val_ds)
preds = preds_output.predictions.argmax(-1)
labels = preds_output.label_ids

# Load label map to get class names
with open(model_path / "label_map.json") as f:
    label_map = json.load(f)
id_to_label = {int(v): k for k, v in label_map.items()}
class_names = [id_to_label[i] for i in range(len(id_to_label))]

# Per-class report
print("\nPER-CLASS BREAKDOWN:")
print(classification_report(labels, preds, target_names=class_names))

# Confusion matrix
cm = confusion_matrix(labels, preds)
cm_df = pd.DataFrame(cm, index=class_names, columns=class_names)
print("\nCONFUSION MATRIX:")
print(cm_df)

print("\n" + "="*30)
print(f"MODEL PERFORMANCE METRICS")
print("="*30)
print(f"Accuracy: {metrics['eval_accuracy']:.4f}")
print(f"F1-Score: {metrics['eval_f1']:.4f}")
print("="*30)