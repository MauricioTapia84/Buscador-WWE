from fastapi import FastAPI
from fastapi import APIRouter
from fastapi import HTTPException
from typing import Optional

app = FastAPI(title="WrestlingData API")

root = APIRouter()


@root.get("/wrestlers")
def list_wrestlers():
    """Return wrestlers from processed CSV if available, otherwise fall back to minimal static examples."""
    import os
    import pandas as pd

    p = os.path.join("data", "processed", "wrestlers_extracted.csv")
    if os.path.exists(p):
        try:
            df = pd.read_csv(p)
            return df.to_dict(orient="records")
        except Exception:
            pass
    return [
        {"id": 1, "name": "John Example", "weight_class": "Heavy"},
        {"id": 2, "name": "Jane Demo", "weight_class": "Light"},
    ]


@root.get("/titles")
def list_titles():
    """Return titles from processed CSV if available, otherwise fall back to static examples."""
    import os
    import pandas as pd

    p = os.path.join("data", "processed", "titles_extracted.csv")
    if os.path.exists(p):
        try:
            df = pd.read_csv(p)
            return df.to_dict(orient="records")
        except Exception:
            pass
    return [
        {"id": 1, "name": "World Championship", "holder": "John Example"},
        {"id": 2, "name": "Tag Team Championship", "holder": "Team Demo"},
    ]


app.include_router(root)


@root.get("/wrestlers/{wrestler_id}")
def get_wrestler(wrestler_id: int):
    wrestlers = list_wrestlers()
    for w in wrestlers:
        if w["id"] == wrestler_id:
            return w
    raise HTTPException(status_code=404, detail="Wrestler not found")


@root.get("/titles/{title_id}")
def get_title(title_id: int):
    titles = list_titles()
    for t in titles:
        if t["id"] == title_id:
            return t
    raise HTTPException(status_code=404, detail="Title not found")


@root.get("/search")
def search(q: Optional[str] = None):
    """Search wrestlers and titles by name containing `q` (case-insensitive)."""
    if not q:
        return {"wrestlers": list_wrestlers(), "titles": list_titles()}
    ql = q.lower()
    ws = [w for w in list_wrestlers() if ql in w["name"].lower()]
    ts = [t for t in list_titles() if ql in t["name"].lower()]
    return {"wrestlers": ws, "titles": ts}


@root.get("/health")
def health():
    return {"status": "ok"}


# include router after all route definitions
app.include_router(root)
