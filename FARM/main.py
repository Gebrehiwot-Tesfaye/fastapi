from fastapi import FastAPI, Path
from typing import Optional,Union

from pydantic import BaseModel




app = FastAPI()

# I Want to create blog
@app.get("/")
def index():
    return {"message": "Welcome to the Blog API"}

@app.get('/blog/{id}')
def show(id: int):
    if id !=    id:
        return("the id is missing")
    return id

    