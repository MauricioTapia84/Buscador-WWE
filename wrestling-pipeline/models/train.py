import json
import logging
from pathlib import Path

import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, f1_score, roc_auc_score
from xgboost import XGBClassifier

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("models.train")


def load_data(filepath: str) -> pd.DataFrame:
    logger.info(f"Cargando datos desde {filepath}")
    return pd.read_csv(filepath)


def build_preprocessor(numeric_features: list[str], categorical_features: list[str]) -> ColumnTransformer:
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
    ])

    transformers = []
    if numeric_features:
        transformers.append(('num', numeric_transformer, numeric_features))
    if categorical_features:
        transformers.append(('cat', categorical_transformer, categorical_features))

    return ColumnTransformer(transformers=transformers, remainder='drop')


def prepare_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, list[str], list[str]]:
    target = 'es_campeon' if 'es_campeon' in df.columns else 'is_champion'
    if target not in df.columns:
        raise ValueError('Dataset must contain es_campeon or is_champion column')

    X = df.copy()
    y = X.pop(target).astype(int)

    candidate_numeric = [
        'total_wins',
        'total_losses',
        'total_matches',
        'win_rate',
    ]
    numeric_features = [col for col in candidate_numeric if col in X.columns]
    categorical_features = [col for col in ['era'] if col in X.columns]

    if not numeric_features:
        raise ValueError('No hay columnas numéricas disponibles para entrenar el modelo.')

    X = X[numeric_features + categorical_features]
    return X, y, numeric_features, categorical_features


def get_xgboost_scale_pos_weight(y: pd.Series) -> float:
    positives = int((y == 1).sum())
    negatives = int((y == 0).sum())
    if positives == 0 or negatives == 0:
        return 1.0
    return max(1.0, negatives / positives)


def train_and_select_model(X_train, y_train, numeric_features: list[str], categorical_features: list[str]):
    logger.info('Construyendo pipeline de preprocesamiento')
    preprocessor = build_preprocessor(numeric_features, categorical_features)

    scale_pos_weight = get_xgboost_scale_pos_weight(y_train)
    candidates = {
        'LogisticRegression': (
            LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
            {'classifier__C': [0.1, 1.0, 10.0]},
        ),
        'RandomForest': (
            RandomForestClassifier(random_state=42, class_weight='balanced'),
            {
                'classifier__n_estimators': [100, 200],
                'classifier__max_depth': [5, 10, None],
                'classifier__min_samples_leaf': [1, 3],
            },
        ),
        'XGBoost': (
            XGBClassifier(
                objective='binary:logistic',
                eval_metric='logloss',
                random_state=42,
                verbosity=0,
                scale_pos_weight=scale_pos_weight,
                n_jobs=-1,
            ),
            {
                'classifier__n_estimators': [100, 200],
                'classifier__learning_rate': [0.01, 0.05, 0.1],
                'classifier__max_depth': [3, 5],
            },
        ),
    }

    best_model = None
    best_score = -1.0
    best_name = None

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    for name, (model, params) in candidates.items():
        logger.info(f'Entrenando {name}')
        pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', model)])
        grid = GridSearchCV(pipeline, params, cv=cv, scoring='f1_macro', n_jobs=-1, error_score='raise')
        grid.fit(X_train, y_train)
        score = grid.best_score_
        logger.info(f'{name} F1 macro = {score:.4f}')
        if score > best_score:
            best_score = score
            best_model = grid.best_estimator_
            best_name = name

    logger.info(f'Mejor modelo: {best_name} con F1={best_score:.4f}')
    return best_model, best_name, best_score


def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
    return {
        'accuracy': accuracy_score(y_test, y_pred),
        'f1_score': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_proba) if y_proba is not None else None,
        'classification_report': classification_report(y_test, y_pred, output_dict=True, zero_division=0),
    }


def save_metrics(metrics: dict, path: str) -> None:
    with open(path, 'w', encoding='utf-8') as handler:
        json.dump(metrics, handler, indent=2, ensure_ascii=False)


def main():
    base = Path(__file__).resolve().parent.parent
    data_path = base / 'data' / 'processed' / 'wrestling_clean.csv'
    df = load_data(str(data_path))

    X, y, numeric_features, categorical_features = prepare_data(df)
    logger.info('Columnas utilizadas para entrenamiento: %s', numeric_features + categorical_features)
    logger.info('Balance de clases: %s', y.value_counts().to_dict())

    stratify = y if y.nunique() > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=stratify
    )

    model, model_name, model_score = train_and_select_model(X_train, y_train, numeric_features, categorical_features)
    metrics = evaluate_model(model, X_test, y_test)
    metrics.update({
        'model_name': model_name,
        'best_score': model_score,
        'feature_columns': numeric_features + categorical_features,
        'class_balance': y.value_counts().to_dict(),
    })

    model_path = base / 'models' / 'champion_predictor.pkl'
    metrics_path = base / 'models' / 'evaluation_report.json'
    joblib.dump(model, model_path)
    save_metrics(metrics, str(metrics_path))
    logger.info(f'Modelo guardado en {model_path}')
    logger.info(f'Métricas guardadas en {metrics_path}')


if __name__ == '__main__':
    main()
