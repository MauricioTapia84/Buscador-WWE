from fastapi import FastAPI
from fastapi import APIRouter
from fastapi import HTTPException
from typing import Optional

app = FastAPI(title="WrestlingData API")

root = APIRouter()


@root.get("/wrestlers")
def list_wrestlers():
    """Return wrestlers from processed CSV if available, otherwise return empty list."""
    import os
    import pandas as pd
    import math

    p = "/app/data/processed/wrestlers_extracted.csv"
    if os.path.exists(p):
        try:
            df = pd.read_csv(p)
            records = df.to_dict(orient="records")
            # Convertir de forma segura todos los NaN de floats a None para compatibilidad JSON
            cleaned_records = []
            for r in records:
                cleaned_r = {}
                for k, v in r.items():
                    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                        cleaned_r[k] = None
                    elif pd.isna(v):
                        cleaned_r[k] = None
                    else:
                        cleaned_r[k] = v
                cleaned_records.append(cleaned_r)
            return cleaned_records
        except Exception:
            pass
    return []


@root.get("/titles")
def list_titles():
    """Return titles from processed CSV if available, otherwise return empty list."""
    import os
    import pandas as pd
    import math

    p = "/app/data/processed/titles_extracted.csv"
    if os.path.exists(p):
        try:
            df = pd.read_csv(p)
            # Convertir fechas a strings para compatibilidad JSON
            if "won_date" in df.columns:
                df["won_date"] = df["won_date"].astype(str)
            records = df.to_dict(orient="records")
            cleaned_records = []
            for r in records:
                cleaned_r = {}
                for k, v in r.items():
                    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                        cleaned_r[k] = None
                    elif pd.isna(v):
                        cleaned_r[k] = None
                    else:
                        cleaned_r[k] = v
                cleaned_records.append(cleaned_r)
            return cleaned_records
        except Exception:
            pass
    return []


app.include_router(root)


@root.get("/wrestlers/{wrestler_id}")
def get_wrestler(wrestler_id: int):
    wrestlers = list_wrestlers()
    for w in wrestlers:
        if w.get("id") == wrestler_id:
            return w
    raise HTTPException(status_code=404, detail="Wrestler not found")


@root.get("/titles/{title_id}")
def get_title(title_id: int):
    titles = list_titles()
    for t in titles:
        if t.get("id") == title_id:
            return t
    raise HTTPException(status_code=404, detail="Title not found")


@root.get("/search")
def search(q: Optional[str] = None):
    """Search wrestlers and titles by query string `q` (case-insensitive)."""
    if not q:
        return {"wrestlers": list_wrestlers(), "titles": list_titles()}
    ql = q.lower()
    
    ws = []
    for w in list_wrestlers():
        if w.get("name") and ql in str(w["name"]).lower():
            ws.append(w)
            
    ts = []
    for t in list_titles():
        # En títulos, la clave puede ser 'title' o 'name'
        title_name = t.get("title") or t.get("name") or ""
        if ql in str(title_name).lower():
            ts.append(t)
            
    return {"wrestlers": ws, "titles": ts}


@root.get("/health")
def health():
    return {"status": "ok"}


# include router after all route definitions
app.include_router(root)
