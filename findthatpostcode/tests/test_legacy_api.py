from findthatpostcode.tests.fixtures import client


def test_postcode():
    response = client.get("/postcodes/AB12+3CD.json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    result = response.json()
    assert result["data"]["attributes"]["pcds"] == "AB12 3CD"
    assert result["data"]["id"] == "AB12 3CD"
    assert result["data"]["links"]["html"] == "postcodes/SW1A+1AA.html"
    assert result["data"]["relationships"]["areas"]["data"][0]["id"] == "E00023938"
    assert (
        result["data"]["relationships"]["nearest_places"]["data"][0]["id"]
        == "IPN0077107"
    )
    assert result["included"][0]["id"] == "E00023938"


def test_points():
    response = client.get("/points/51.501009,-0.141588.json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    result = response.json()
    assert result["data"]["attributes"]["distance_from_postcode"] == 0
    assert result["data"]["id"] == [51.501009, -0.141588]
    assert result["included"][0]["id"] == "SW1A 1AA"


def test_area():
    response = client.get("/areas/E14000639.json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    result = response.json()
    assert result["data"]["attributes"]["name"] == "Cities of London and Westminster"
    assert result["data"]["id"] == "E14000639"


def test_area_boundaries():
    response = client.get("/areas/E14000639.geojson")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    result = response.json()
    assert result["features"]["geometry"]["coordinates"]["type"] == "MultiPolygon"
    assert (
        result["features"]["properties"]["name"] == "Cities of London and Westminster"
    )
    assert result["features"]["properties"]["code"] == "E14000639"


def test_place():
    response = client.get("/places/IPN0000543.json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    result = response.json()
    assert result["data"]["attributes"]["name"] == "Adams Green"
    assert result["data"]["id"] == "IPN0000543"


def test_areatype():
    response = client.get("/areatypes/pcon.json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    result = response.json()
    assert (
        result["data"]["attributes"]["name"] == "Westminster parliamentary constituency"
    )
    assert result["data"]["attributes"]["entities"][3] == "W07"
    assert result["data"]["id"] == "pcon"
