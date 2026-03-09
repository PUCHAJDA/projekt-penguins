"""
Etap 3: Trenowanie modelu — Optuna + MLflow.

- Funkcja celu z 4 hiperparametrami (n_estimators, max_depth,
  min_samples_split, min_samples_leaf)
- cross_val_score (5-fold) jako metryka Optuna
- MLflowCallback — automatyczne logowanie prób
- Eksperyment: "penguins-optuna", >= 20 prób
- Najlepszy model zapisany do models/model.pkl
"""

import os
import pickle

import mlflow
import optuna
import pandas as pd
import yaml
from optuna.integration.mlflow import MLflowCallback
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

TARGET_COL = "species"


def main():
    with open("params.yaml", "r") as f:
        params = yaml.safe_load(f)

    n_trials = params["train"]["n_trials"]
    cv_folds = params["train"]["cv_folds"]
    experiment_name = params["train"]["experiment_name"]

    print("Wczytywanie data/train.csv...")
    train_df = pd.read_csv("data/train.csv")
    X_train = train_df.drop(columns=[TARGET_COL])
    y_train = train_df[TARGET_COL]
    print(f"Zbior treningowy: {X_train.shape[0]} probek, {X_train.shape[1]} cech")

    mlflow.set_experiment(experiment_name)

    mlflow_callback = MLflowCallback(
        tracking_uri=mlflow.get_tracking_uri(),
        metric_name="cv_accuracy",
    )

    def objective(trial):
        n_estimators = trial.suggest_int("n_estimators", 50, 300, step=50)
        max_depth = trial.suggest_int("max_depth", 3, 15)
        min_samples_split = trial.suggest_int("min_samples_split", 2, 10)
        min_samples_leaf = trial.suggest_int("min_samples_leaf", 1, 5)

        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=42,
        )
        scores = cross_val_score(
            model, X_train, y_train, cv=cv_folds, scoring="accuracy"
        )
        return scores.mean()

    study = optuna.create_study(
        direction="maximize",
        study_name=experiment_name,
        pruner=optuna.pruners.MedianPruner(n_warmup_steps=5),
    )
    print(f"Uruchamianie {n_trials} prob Optuna w eksperymencie '{experiment_name}'...")
    study.optimize(objective, n_trials=n_trials, callbacks=[mlflow_callback])

    print(f"Najlepsze hiperparametry: {study.best_params}")
    print(f"Najlepsza CV accuracy: {study.best_value:.4f}")

    best_model = RandomForestClassifier(**study.best_params, random_state=42)
    best_model.fit(X_train, y_train)

    os.makedirs("models", exist_ok=True)
    model_path = "models/model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(best_model, f)
    print(f"Najlepszy model zapisany do: {model_path}")


if __name__ == "__main__":
    main()
