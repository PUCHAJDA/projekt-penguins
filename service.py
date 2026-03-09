"""
Serwis BentoML — klasyfikacja gatunkow pingwinow Palmer.

Laduje penguins_classifier i penguins_encoder z BentoML store.
Preprocessing identyczny jak w pipeline (encoder.pkl).
"""

import bentoml
import numpy as np
from bentoml.models import BentoModel
from pydantic import BaseModel


class PenguinFeatures(BaseModel):
    culmen_length_mm: float
    culmen_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float
    sex: str    # "MALE" / "FEMALE"
    island: str  # "Biscoe" / "Dream" / "Torgersen"


NUM_COLS_ORDER = ["culmen_length_mm", "culmen_depth_mm", "flipper_length_mm", "body_mass_g"]
CAT_COLS_ORDER = ["island", "sex"]


@bentoml.service(name="penguins_classifier_service")
class PenguinsService:
    penguins_model = BentoModel("penguins_classifier:latest")
    penguins_encoder = BentoModel("penguins_encoder:latest")

    def __init__(self):
        self.model = bentoml.sklearn.load_model(self.penguins_model)
        self.encoder = bentoml.sklearn.load_model(self.penguins_encoder)

    @bentoml.api()
    def predict(self, features: PenguinFeatures) -> dict:
        num_data = np.array([[
            features.culmen_length_mm,
            features.culmen_depth_mm,
            features.flipper_length_mm,
            features.body_mass_g,
        ]])

        cat_data = [[features.island, features.sex]]
        cat_encoded = self.encoder.transform(cat_data)

        X = np.hstack([num_data, cat_encoded])
        prediction = self.model.predict(X)
        return {"species": str(prediction[0])}
