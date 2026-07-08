import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, f1_score, accuracy_score


def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    if X_test is None or X_test.empty or y_test is None or y_test.empty:
        return {}

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None

    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    result = {
        'accuracy': accuracy_score(y_test, y_pred),
        'f1_score': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_proba) if y_proba is not None else None,
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        'classification_report': report,
    }
    return result
