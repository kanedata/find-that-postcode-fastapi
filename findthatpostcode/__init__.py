from fastapi import FastAPI

from findthatpostcode import api, graphql

app = FastAPI()

app.include_router(api.router)
app.include_router(graphql.router, prefix="/graphql")


@app.get("/")
def read_root():
    return {"Hello": "World"}
