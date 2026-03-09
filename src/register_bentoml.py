"""
Etap 5: Rejestracja modelu i encodera w BentoML store.

- Laduje models/model.pkl i models/encoder.pkl
- Zapisuje jako bentoml.sklearn modele: penguins_classifier, penguins_encoder
- Loguje rejestracje do MLflow
"""

import pickle

import bentoml
import mlflow
import yaml


def main():
    with open("params.yaml", "r") as f:
        params = yaml.safe_load(f)

    experiment_name = params["train"]["experiment_name"]

    print("Ladowanie models/model.pkl i models/encoder.pkl...")
    with open("models/model.pkl", "rb") as f:
        model = pickle.load(f)

    with open("models/encoder.pkl", "rb") as f:
        encoder = pickle.load(f)

    model_tag = bentoml.sklearn.save_model(
        "penguins_classifier",
        model,
        signatures={"predict": {"batchable": True, "batch_dim": 0}},
        metadata={"params": str(model.get_params())},
    )
    print(f"Model zarejestrowany w BentoML: {model_tag}")

    encoder_tag = bentoml.sklearn.save_model(
        "penguins_encoder",
        encoder,
        signatures={"transform": {"batchable": True, "batch_dim": 0}},
    )
    print(f"Encoder zarejestrowany w BentoML: {encoder_tag}")

    mlflow.set_experiment(experiment_name)
    with mlflow.start_run(run_name="bentoml-registration"):
        mlflow.log_param("model_tag", str(model_tag))
        mlflow.log_param("encoder_tag", str(encoder_tag))
        print("Rejestracja zalogowana do MLflow.")


if __name__ == "__main__":
    main()
