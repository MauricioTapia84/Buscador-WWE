
from pydantic import BaseModel

class Wrestler(BaseModel):

    name: str

    height: str | None = None

    weight: str | None = None


def validate_wrestler(data):

    try:
        Wrestler(**data)
        return True

    except Exception as e:

        print(e)

        return False