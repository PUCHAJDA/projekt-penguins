"""
Etap 2: Przygotowanie danych Palmer Penguins.

- dropna() — usuwanie brakujacych wartosci
- OneHotEncoder dla zmiennych kategorycznych (island, sex)
- Podzial na zbior treningowy i testowy
- Zapis: data/train.csv, data/test.csv, models/encoder.pkl
"""

import os
import pickle

import numpy as np
import pandas as pd
import yaml
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

NUM_COLS = ["culmen_length_mm", "culmen_depth_mm", "flipper_length_mm", "body_mass_g"]
CAT_COLS = ["island", "sex"]
TARGET_COL = "species"


def main():
    with open("params.yaml", "r") as f:
        params = yaml.safe_load(f)

    test_size = params["data"]["test_size"]
    random_state = params["data"]["random_state"]

    print("Wczytywanie data/penguins.csv...")
    df = pd.read_csv("data/penguins.csv")
    print(f"Przed dropna: {len(df)} rekordow")

    df = df.dropna(subset=NUM_COLS + CAT_COLS + [TARGET_COL])
    print(f"Po dropna: {len(df)} rekordow")

    X_num = df[NUM_COLS].astype(float).values
    y = df[TARGET_COL].values

    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    X_cat = encoder.fit_transform(df[CAT_COLS])
    cat_feature_names = list(encoder.get_feature_names_out(CAT_COLS))

    X_all = np.hstack([X_num, X_cat])
    all_cols = NUM_COLS + cat_feature_names

    full_df = pd.DataFrame(X_all, columns=all_cols)
    full_df[TARGET_COL] = y

    train_df, test_df = train_test_split(
        full_df, test_size=test_size, random_state=random_state, stratify=full_df[TARGET_COL]
    )
    print(f"Zbior treningowy: {len(train_df)}, testowy: {len(test_df)}")

    os.makedirs("models", exist_ok=True)

    train_df.to_csv("data/train.csv", index=False)
    test_df.to_csv("data/test.csv", index=False)
    print("Zapisano data/train.csv i data/test.csv")

    encoder_path = "models/encoder.pkl"
    with open(encoder_path, "wb") as f:
        pickle.dump(encoder, f)
    print(f"Encoder zapisany do: {encoder_path}")
    print(f"Kategorie encodera: {encoder.categories_}")


if __name__ == "__main__":
    main()
