import pytest
from fastapi.testclient import TestClient

from findthatpostcode.crud import Area, Postcode
from findthatpostcode.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Find that Postcode" in response.text
    assert "Search" in response.text


def test_read_about():
    response = client.get("/about")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "About this site" in response.text
