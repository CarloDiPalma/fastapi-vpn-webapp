from typing import Optional

from fastapi import FastAPI, Body, Response, status, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    if not item_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='message')
    return {"item_id": item_id}


@app.post("/something")
def create_something(payload: dict = Body(...)):
    print(payload)
    return {"asdsad": "asdas"}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_something(post: Post):
    print(post.dict())
    return {"asdsad": "asdas"}
