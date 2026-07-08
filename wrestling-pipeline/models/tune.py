from sklearn.model_selection import GridSearchCV


def tune_hyperparameters(pipeline, X, y, params: dict, cv: int = 5, scoring: str = 'f1_macro'):
    grid = GridSearchCV(pipeline, params, cv=cv, scoring=scoring, n_jobs=-1)
    grid.fit(X, y)
    return grid
