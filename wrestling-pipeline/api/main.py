from fastapi import FastAPI
from fastapi import APIRouter

app = FastAPI(title="WrestlingData API")

root = APIRouter()


@root.get("/wrestlers")
def list_wrestlers():
    return [
        {"id": 1, "name": "John Example", "weight_class": "Heavy"},
        {"id": 2, "name": "Jane Demo", "weight_class": "Light"},
    ]


@root.get("/titles")
def list_titles():
    return [
        {"id": 1, "name": "World Championship", "holder": "John Example"},
        {"id": 2, "name": "Tag Team Championship", "holder": "Team Demo"},
    ]


app.include_router(root)
