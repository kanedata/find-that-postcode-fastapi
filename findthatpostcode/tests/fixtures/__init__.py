import os

from findthatpostcode.settings import CHD_URL, MSOA_URL, NSPL_URL, RGC_URL

MOCK_FILES = {
    CHD_URL: os.path.join(
        os.path.dirname(__file__),
        "chd.zip",
    ),
    MSOA_URL: os.path.join(os.path.dirname(__file__), "msoanames.csv"),
    RGC_URL: os.path.join(
        os.path.dirname(__file__),
        "rgc.zip",
    ),
    NSPL_URL: os.path.join(
        os.path.dirname(__file__),
        "nspl21.zip",
    ),
}


def mock_bulk(es, records, **kwargs):
    return len(records), []


class MockES:
    def __init__(self):
        self._index = {}
        self._index_name = None

    def index(self, index_name, doc_type, body, id):
        self._index_name = index_name
        self._index[id] = body

    def get(self, index_name, doc_type, id):
        return self._index[id]

    def search(self, index_name, doc_type, body):
        return {
            "hits": {
                "hits": [
                    {"_source": self._index[id]}
                    for id in body["query"]["ids"]["values"]
                ]
            }
        }
