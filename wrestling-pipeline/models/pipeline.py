from sklearn.pipeline import Pipeline

from .preprocess import build_preprocessing_pipeline


def build_model_pipeline(model, numeric_features: list[str], categorical_features: list[str]) -> Pipeline:
    preprocessor = build_preprocessing_pipeline(numeric_features, categorical_features)
    return Pipeline(
        steps=[
            ('preprocessor', preprocessor),
            ('classifier', model),
        ]
    )
