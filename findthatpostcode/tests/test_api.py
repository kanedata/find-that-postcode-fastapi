from fastapi.testclient import TestClient
from findthatpostcode.main import app
from findthatpostcode.crud import Postcode, Area
import pytest

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Find that Postcode" in response.text


@pytest.mark.parametrize(
    "postcode",
    [
        "SE1 1AA",
    ],
)
def test_get_postcode(postcode, monkeypatch):

    monkeypatch.setattr(
        Postcode, "get", lambda *args, **kwargs: Postcode(pcds=kwargs["id"])
    )
    monkeypatch.setattr(Area, "mget", lambda *args, **kwargs: [Area()])

    response = client.get(f"/api/v1/postcodes/{postcode}.json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    result = response.json()
    assert result["pcds"] == postcode
