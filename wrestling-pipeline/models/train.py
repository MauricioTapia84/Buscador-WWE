import pandas as pd
import numpy as np
import os
import joblib
import logging
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score, f1_score

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("models.train")

def load_data(filepath: str):
    logger.info(f"Cargando datos desde {filepath}")
    df = pd.read_csv(filepath)
    return df

def build_pipeline():
    logger.info("Construyendo Feature Engineering Pipeline")
    numeric_features = ['total_wins', 'total_losses', 'total_matches', 'win_rate']
    categorical_features = [] # Si tuvieramos país, iría acá. Por simplicidad usamos solo las generadas.
    
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features)
        ])
    return preprocessor

def train_models(X_train, y_train):
    logger.info("Iniciando entrenamiento de modelos")
    preprocessor = build_pipeline()
    
    models = {
        'LogisticRegression': (LogisticRegression(max_iter=1000), {
            'classifier__C': [0.1, 1, 10]
        }),
        'RandomForest': (RandomForestClassifier(random_state=42), {
            'classifier__n_estimators': [50, 100],
            'classifier__max_depth': [5, 10, None]
        }),
        'XGBoost': (XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42), {
            'classifier__n_estimators': [50, 100],
            'classifier__learning_rate': [0.01, 0.1]
        })
    }
    
    best_model = None
    best_score = 0
    best_model_name = ""
    
    for name, (model, params) in models.items():
        logger.info(f"Entrenando {name} con GridSearchCV...")
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', model)
        ])
        
        # Usar f1_macro porque las clases están desbalanceadas
        grid = GridSearchCV(pipeline, params, cv=3, scoring='f1_macro', n_jobs=-1)
        grid.fit(X_train, y_train)
        
        score = grid.best_score_
        logger.info(f"{name} Mejor F1 Score: {score:.4f}")
        
        if score > best_score:
            best_score = score
            best_model = grid.best_estimator_
            best_model_name = name
            
    logger.info(f"🏆 El mejor modelo es {best_model_name} con F1={best_score:.4f}")
    return best_model

def evaluate_and_save(model, X_test, y_test, out_path: str):
    logger.info("Evaluando el mejor modelo en el conjunto de prueba")
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
    
    logger.info("\n" + classification_report(y_test, y_pred))
    if y_proba is not None:
        auc = roc_auc_score(y_test, y_proba)
        logger.info(f"AUC-ROC: {auc:.4f}")
        
    logger.info(f"Guardando modelo en {out_path}")
    joblib.dump(model, out_path)

def main():
    data_path = os.path.join('..', 'data', 'processed', 'wrestling_clean.csv')
    df = load_data(data_path)
    
    # Prevenir Data Leakage: Split antes de cualquier otra cosa
    logger.info("Separando datos (Train/Test Split 80/20)")
    X = df[['total_wins', 'total_losses', 'total_matches', 'win_rate']]
    y = df['is_champion']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    best_model = train_models(X_train, y_train)
    
    model_path = os.path.join(os.path.dirname(__file__), 'champion_predictor.pkl')
    evaluate_and_save(best_model, X_test, y_test, model_path)

if __name__ == '__main__':
    main()
