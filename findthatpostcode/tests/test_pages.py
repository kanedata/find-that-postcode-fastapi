from findthatpostcode.tests.fixtures import client


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Find that Postcode" in response.text
    assert "Search" in response.text


def test_about():
    response = client.get("/about")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "About this site" in response.text


def test_search():
    response = client.get("/search")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Search for an area name" in response.text
    assert "Use your location" in response.text


def test_search_q():
    response = client.get("/search/?q=Test")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Test Valley" in response.text
    assert 'results for "Test"' in response.text


def test_area_html():
    response = client.get("/areas/E07000093.html")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Test Valley" in response.text
    assert "E07000093" in response.text
    assert "Example postcodes" in response.text


def test_postcode_html():
    response = client.get("/postcodes/SW1A%201AA.html")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "SW1A 1AA" in response.text
    assert "E09000033" in response.text


def test_point_html():
    response = client.get("/points/51.501009,-0.141588.html")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "SW1A 1AA" in response.text
    assert "Point 51.50101, -0.14159" in response.text


def test_place_html():
    response = client.get("/places/IPN0000543.html")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Adams Green" in response.text
    assert "Locality in Great Britain" in response.text


def test_areatype_html():
    response = client.get("/areatypes/pcon.html")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Westminster parliamentary constituency" in response.text
    assert "E14XXXXXX" in response.text


def test_areatypes_html():
    response = client.get("/areatypes/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Westminster parliamentary constituency" in response.text
    assert "Browse by area type" in response.text


def test_addtocsv():
    response = client.get("/addtocsv/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Add fields to CSV" in response.text
    assert (
        "Therefore it is recommended that you think carefully before using this tool with any personal or sensitive data."
        in response.text
    )


def test_combine_geojson():
    response = client.get("/tools/merge-geojson")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Combine GeoJSON files" in response.text


def test_reduce_geojson():
    response = client.get("/tools/reduce-geojson")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Reduce GeoJSON file size" in response.text
