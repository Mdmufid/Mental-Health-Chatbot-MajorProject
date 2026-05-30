"""
Downloads dair-ai/emotion, merges with existing data,
balances classes and saves to emotion_model/data/processed/
"""

import pandas as pd
from pathlib import Path
from datasets import load_dataset
from sklearn.utils import resample

# ── Paths ──────────────────────────────────────────
RAW_TRAIN = Path("emotion_model/data/processed/train.csv")
RAW_VAL   = Path("emotion_model/data/processed/val.csv")
RAW_TEST  = Path("emotion_model/data/processed/test.csv")
OUT_DIR = Path("emotion_model/data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Label maps ─────────────────────────────────────
NUMERIC_BROAD_MAP = {
    0:"joy",
    1:"joy",
    2:"anger",
    3:"anger",
    4:"joy",
    5:"love",
    6:"neutral",
    7:"neutral",
    8:"love",
    9:"sadness",
    10:"anger",
    11:"anger",
    12:"sadness",
    13:"joy",
    14:"fear",
    15:"joy",
    16:"sadness",
    17:"joy",
    18:"love",
    19:"fear",
    20:"neutral",
    21:"joy",
    22:"joy",
    23:"neutral",
    24:"joy",
    25:"sadness",
    26:"sadness",
    27:"neutral",
}

DAIR_LABEL_MAP = {
    0:"sadness",
    1:"joy",
    2:"love",
    3:"anger",
    4:"fear",
    5:"neutral",
}

def load_existing():
    train = pd.read_csv(RAW_TRAIN).dropna(subset=["text","label"])
    val = pd.read_csv(RAW_VAL).dropna(subset=["text","label"])
    test = pd.read_csv(RAW_TEST).dropna(subset=["text","label"])

    train = train[train["text"].str.strip() != ""]
    val = val[val["text"].str.strip() != ""]
    test = test[test["text"].str.strip() != ""]

    train["label"] = train["label"].map(NUMERIC_BROAD_MAP)
    val["label"] = val["label"].map(NUMERIC_BROAD_MAP)
    test["label"] = test["label"].map(NUMERIC_BROAD_MAP)

    return train.dropna(subset=["label"]), val.dropna(subset=["label"]), test.dropna(subset=["label"])

def load_dair():
    ds = load_dataset("dair-ai/emotion")

    train = ds["train"].to_pandas()[["text","label"]]
    val = ds["validation"].to_pandas()[["text","label"]]
    test = ds["test"].to_pandas()[["text","label"]]

    train["label"] = train["label"].map(DAIR_LABEL_MAP)
    val["label"] = val["label"].map(DAIR_LABEL_MAP)
    test["label"] = test["label"].map(DAIR_LABEL_MAP)

    return train, val, test

def merge(existing, new):
    merged = pd.concat([existing[["text","label"]], new[["text","label"]]],
                       ignore_index=True).drop_duplicates(subset=["text"])
    return merged.sample(frac=1, random_state=42).reset_index(drop=True)

def balance(df):
    max_count = df["label"].value_counts().max()
    parts = []
    for _, group in df.groupby("label"):
        if len(group) < max_count:
            group = resample(group, replace=True,
                             n_samples=max_count, random_state=42)
        parts.append(group)
    return pd.concat(parts).sample(frac=1, random_state=42).reset_index(drop=True)

if __name__ == "__main__":
    print("📂 Loading existing data...")
    ex_train, ex_val, ex_test = load_existing()

    print("🌐 Downloading dair-ai/emotion...")
    dair_train, dair_val, dair_test = load_dair()

    print("🔀 Merging...")
    train_df = merge(ex_train, dair_train)
    val_df = merge(ex_val,   dair_val)
    test_df = merge(ex_test, dair_test)   # no balancing on test set

    print("⚖️  Balancing training set...")
    train_df = balance(train_df)

    train_df.to_csv(OUT_DIR / "train_v3.csv", index=False)
    val_df.to_csv(OUT_DIR / "val_v3.csv",   index=False)
    test_df.to_csv(OUT_DIR / "test_v3.csv", index=False)

    print(f"\n✅ Saved to {OUT_DIR}")
    print(f"Train: {len(train_df)} | Validation: {len(val_df)} | Test: {len(test_df)}")
    print("\nLabel distribution:")
    print(train_df["label"].value_counts())