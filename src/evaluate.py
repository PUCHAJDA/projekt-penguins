"""
Etap 4: Ewaluacja modelu.

- Laduje models/model.pkl i data/test.csv
- Metryki: accuracy + f1_score(average="weighted")
- Zapis do metrics.json (DVC metrics)
- MLflow run "best-model" z parametrami, metrykami i modelem z sygnatura
"""

import json
import pickle

import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
from mlflow.models import infer_signature
from sklearn.metrics import accuracy_score, f1_score

TARGET_COL = "species"


def main():
    with open("params.yaml", "r") as f:
        params = yaml.safe_load(f)

    experiment_name = params["train"]["experiment_name"]

    print("Wczytywanie data/test.csv i models/model.pkl...")
    test_df = pd.read_csv("data/test.csv")
    X_test = test_df.drop(columns=[TARGET_COL])
    y_test = test_df[TARGET_COL]

    with open("models/model.pkl", "rb") as f:
        model = pickle.load(f)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1-score (weighted): {f1:.4f}")

    metrics = {
        "accuracy": round(accuracy, 4),
        "f1_score": round(f1, 4),
    }
    with open("metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print("Metryki zapisane do: metrics.json")

    mlflow.set_experiment(experiment_name)
    with mlflow.start_run(run_name="best-model"):
        mlflow.log_params(model.get_params())
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1_score_weighted", f1)

        signature = infer_signature(X_test, y_pred)
        mlflow.sklearn.log_model(model, "model", signature=signature)
        print("Zalogowano run 'best-model' do MLflow.")


if __name__ == "__main__":
    main()
