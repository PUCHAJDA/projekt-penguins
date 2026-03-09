"""
Etap 1: Pobieranie danych Palmer Penguins z OpenML.

Odczytuje id zbioru z params.yaml, pobiera dane i zapisuje jako CSV.
"""

import os

import yaml
from sklearn.datasets import fetch_openml


def main():
    with open("params.yaml", "r") as f:
        params = yaml.safe_load(f)

    openml_id = params["data"]["openml_id"]

    print(f"Pobieranie zbioru Palmer Penguins (OpenML id={openml_id})...")
    data = fetch_openml(data_id=openml_id, as_frame=True)
    df = data.frame

    print(f"Pobrano {len(df)} rekordow, kolumny: {list(df.columns)}")

    os.makedirs("data", exist_ok=True)
    output_path = "data/penguins.csv"
    df.to_csv(output_path, index=False)
    print(f"Dane zapisane do: {output_path}")


if __name__ == "__main__":
    main()
