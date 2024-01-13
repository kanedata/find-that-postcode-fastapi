from findthatpostcode.tests.fixtures import client


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Find that Postcode" in response.text
