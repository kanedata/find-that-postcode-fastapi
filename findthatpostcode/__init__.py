from fastapi import FastAPI

from findthatpostcode import api, graphql

app = FastAPI(
    title="Find that Postcode API",
    # description=description,
    version="0.0.1",
    # terms_of_service="http://example.com/terms/",
    contact={
        "name": "David Kane",
        "url": "https://dkane.net/",
        "email": "info@findthatpostcode.uk",
    },
    openapi_tags=[
        {
            "name": "Get postcode",
            "description": "Postcode lookup",
        }
    ]
    # license_info={
    #     "name": "Apache 2.0",
    #     "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    # },
)

app.include_router(api.router)
app.include_router(graphql.router, prefix="/graphql")


@app.get("/")
def read_root():
    return {"Hello": "World"}
