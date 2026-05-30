"""
Quick test — type a sentence and see the predicted emotion.
"""

import json, torch
from pathlib import Path
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

MODEL_PATH = Path("emotion_model/models/transformer_model_v3")

tokenizer = DistilBertTokenizerFast.from_pretrained(str(MODEL_PATH))
model     = DistilBertForSequenceClassification.from_pretrained(str(MODEL_PATH))
model.eval()

with open(MODEL_PATH / "label_map.json") as f:
    label_map = json.load(f)
id_to_label = {int(v): k for k, v in label_map.items()}

def predict(text):
    inputs = tokenizer(text, return_tensors="pt",
                       truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        logits = model(**inputs).logits
    pred = int(torch.argmax(logits, dim=-1))
    return id_to_label.get(pred, "neutral")

if __name__ == "__main__":
    print("🧠 Emotion Predictor — type 'quit' to exit\n")
    while True:
        text = input("You: ").strip()
        if text.lower() == "quit":
            break
        print(f"Emotion: {predict(text)}\n")