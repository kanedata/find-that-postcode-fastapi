import json
import os

from dotenv import load_dotenv

load_dotenv()


def get_es_url(default: str) -> str:
    potential_env_vars = ["ELASTICSEARCH_URL", "ES_URL", "BONSAI_URL"]
    for e_v in potential_env_vars:
        e_v_value = os.environ.get(e_v)
        if e_v_value:
            return e_v_value
    return default


DEBUG = os.environ.get("DEBUG", "false").lower().strip()[0] == "t"
DATABASE_URL = os.environ.get("DATABASE_URL")
ES_URL = get_es_url("http://localhost:9200")
ES_INDEX_PREFIX = os.environ.get("ES_INDEX_PREFIX", "geo")
ES_INDICES = {
    "area": str(ES_INDEX_PREFIX) + "_area",
    "areatype": str(ES_INDEX_PREFIX) + "_entity",
    "postcode": str(ES_INDEX_PREFIX) + "_postcode",
    "placename": str(ES_INDEX_PREFIX) + "_placename",
    "uprn": str(ES_INDEX_PREFIX) + "_uprn",
}
DEFAULT_ENCODING = "latin1"

# S3 Storage settings
S3_REGION = os.environ.get("S3_REGION")
S3_ENDPOINT = os.environ.get("S3_ENDPOINT")
S3_ACCESS_ID = os.environ.get("S3_ACCESS_ID")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")
S3_BUCKET = os.environ.get("S3_BUCKET", "geo-boundaries")

# postcode data URLs
NSPL_URL = "https://www.arcgis.com/sharing/rest/content/items/677cfc3ef56541999314efc795664ce9/data"
ONSPD_URL = "https://www.arcgis.com/sharing/rest/content/items/a644dd04d18f4592b7d36705f93270d8/data"
NHSPD_URL = "https://www.arcgis.com/sharing/rest/content/items/c290e7ec05d542e1a38d0822aaf3e634/data"
PCON_URL = "https://www.arcgis.com/sharing/rest/content/items/0ce50b21cd5a4599b6df0452f7fed235/data"

# area data URLs
RGC_URL = "https://www.arcgis.com/sharing/rest/content/items/7216e9b54a1b49459aaaf59b3f122abc/data"
CHD_URL = "https://www.arcgis.com/sharing/rest/content/items/e2b210c49bd440b89667294ffbe61fa8/data"
MSOA_URL = "https://houseofcommonslibrary.github.io/msoanames/MSOA-Names-Latest.csv"

# placenames data URLs
PLACENAMES_URL = "https://www.arcgis.com/sharing/rest/content/items/e8e725daf8944af6a336a9d183114697/data"

# Stats Urls
IMD2019_URL = "https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/845345/File_7_-_All_IoD2019_Scores__Ranks__Deciles_and_Population_Denominators_3.csv"
IMD2015_URL = "https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/467774/File_7_ID_2015_All_ranks__deciles_and_scores_for_the_Indices_of_Deprivation__and_population_denominators.csv"


with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "areatypes.json")
) as a:
    AREA_TYPES = json.load(a)
    for k in AREA_TYPES:
        AREA_TYPES[k]["countries"] = list(
            set([e[0] for e in AREA_TYPES[k]["entities"]])
        )
    AREA_THEMES = list(set([a["theme"] for a in AREA_TYPES.values()]))
    ENTITIES = {e: k for k, v in AREA_TYPES.items() for e in v["entities"]}

KEY_AREA_TYPES = [
    ("Key", ["ctry", "rgn", "cty", "laua", "ward", "msoa11", "pcon"]),
    ("Secondary", ["ttwa", "pfa", "lep", "lsoa11", "oa11", "npark"]),
    ("Health", ["ccg", "nhser", "lhb"]),
    ("Other", ["bua11", "wz11"]),
]

OTHER_CODES = {
    "osgrdind": [
        "",  # no code 0
        "within the building of the matched address closest to the postcode mean",
        "as for status value 1, except by visual inspection of Landline maps (Scotland only)",
        "approximate to within 50 metres",
        "postcode unit mean (mean of matched addresses with the same postcode, but not snapped to a building)",
        "imputed by ONS, by reference to surrounding postcode grid references",
        "postcode sector mean, (mainly PO Boxes)",
        "",  # code 7 missing
        "postcode terminated prior to Gridlink(R) initiative, last known ONS postcode grid reference",
        "no grid reference available",
    ],
    "usertype": ["Small user", "Large user"],
    "imd": {
        "E92000001": 32844,
        "W92000004": 1909,
        "S92000003": 6976,
        "N92000002": None,
        "L93000001": None,
        "M83000003": None,
    },
}


DEFAULT_UPLOAD_FIELDS = ["latlng", "laua", "laua_name", "rgn", "rgn_name"]
BASIC_UPLOAD_FIELDS = [
    ("latlng", "Latitude / Longitude", False),
    ("estnrth", "OS Easting / Northing", False),
    ("pcds", "Standardised postcode", False),
    ("oac11", "2011 Output Area Classification (OAC)", True),
    ("ru11ind", "2011 Census rural-urban classification", True),
]
STATS_FIELDS = [
    (
        "imd2019_rank",
        "Index of multiple deprivation (2019) rank",
        False,
        "stats.imd2019.imd_rank",
    ),
    (
        "imd2019_decile",
        "Index of multiple deprivation (2019) decile",
        False,
        "stats.imd2019.imd_decile",
    ),
    (
        "imd2015_rank",
        "Index of multiple deprivation (2015) rank",
        False,
        "stats.imd2015.imd_rank",
    ),
    (
        "imd2015_decile",
        "Index of multiple deprivation (2015) decile",
        False,
        "stats.imd2015.imd_decile",
    ),
    # ("popn", "Total population (2015)", False, "stats.population2015.population_total"),
]

# "Supergroup", "Group", "Subgroup"],
OAC11_CODE = {
    "1A1": ["Rural residents", "Farming communities", "Rural workers and families"],
    "1A2": [
        "Rural residents",
        "Farming communities",
        "Established farming communities",
    ],
    "1A3": ["Rural residents", "Farming communities", "Agricultural communities"],
    "1A4": ["Rural residents", "Farming communities", "Older farming communities"],
    "1B1": ["Rural residents", "Rural tenants", "Rural life"],
    "1B2": ["Rural residents", "Rural tenants", "Rural white-collar workers"],
    "1B3": ["Rural residents", "Rural tenants", "Ageing rural flat tenants"],
    "1C1": [
        "Rural residents",
        "Ageing rural dwellers",
        "Rural employment and retirees",
    ],
    "1C2": ["Rural residents", "Ageing rural dwellers", "Renting rural retirement"],
    "1C3": ["Rural residents", "Ageing rural dwellers", "Detached rural retirement"],
    "2A1": ["Cosmopolitans", "Students around campus", "Student communal living"],
    "2A2": ["Cosmopolitans", "Students around campus", "Student digs"],
    "2A3": ["Cosmopolitans", "Students around campus", "Students and professionals"],
    "2B1": ["Cosmopolitans", "Inner city students", "Students and commuters"],
    "2B2": [
        "Cosmopolitans",
        "Inner city students",
        "Multicultural student neighbourhood",
    ],
    "2C1": ["Cosmopolitans", "Comfortable cosmopolitan", "Migrant families"],
    "2C2": ["Cosmopolitans", "Comfortable cosmopolitan", "Migrant commuters"],
    "2C3": [
        "Cosmopolitans",
        "Comfortable cosmopolitan",
        "Professional service cosmopolitans",
    ],
    "2D1": ["Cosmopolitans", "Aspiring and affluent", "Urban cultural mix"],
    "2D2": [
        "Cosmopolitans",
        "Aspiring and affluent",
        "Highly-qualified quaternary workers",
    ],
    "2D3": ["Cosmopolitans", "Aspiring and affluent", "EU white-collar workers"],
    "3A1": ["Ethnicity central", "Ethnic family life", "Established renting families"],
    "3A2": ["Ethnicity central", "Ethnic family life", "Young families and students"],
    "3B1": ["Ethnicity central", "Endeavouring ethnic mix", "Striving service workers"],
    "3B2": [
        "Ethnicity central",
        "Endeavouring ethnic mix",
        "Bangladeshi mixed employment",
    ],
    "3B3": [
        "Ethnicity central",
        "Endeavouring ethnic mix",
        "Multi-ethnic professional service workers",
    ],
    "3C1": ["Ethnicity central", "Ethnic dynamics", "Constrained neighbourhoods"],
    "3C2": ["Ethnicity central", "Ethnic dynamics", "Constrained commuters"],
    "3D1": ["Ethnicity central", "Aspirational techies", "New EU tech workers"],
    "3D2": ["Ethnicity central", "Aspirational techies", "Established tech workers"],
    "3D3": ["Ethnicity central", "Aspirational techies", "Old EU tech workers"],
    "4A1": [
        "Multicultural metropolitans",
        "Rented family living",
        "Social renting young families",
    ],
    "4A2": [
        "Multicultural metropolitans",
        "Rented family living",
        "Private renting new arrivals",
    ],
    "4A3": [
        "Multicultural metropolitans",
        "Rented family living",
        "Commuters with young families",
    ],
    "4B1": [
        "Multicultural metropolitans",
        "Challenged Asian terraces",
        "Asian terraces and flats",
    ],
    "4B2": [
        "Multicultural metropolitans",
        "Challenged Asian terraces",
        "Pakistani communities",
    ],
    "4C1": ["Multicultural metropolitans", "Asian traits", "Achieving minorities"],
    "4C2": [
        "Multicultural metropolitans",
        "Asian traits",
        "Multicultural new arrivals",
    ],
    "4C3": ["Multicultural metropolitans", "Asian traits", "Inner city ethnic mix"],
    "5A1": ["Urbanites", "Urban professionals and families", "White professionals"],
    "5A2": [
        "Urbanites",
        "Urban professionals and families",
        "Multi-ethnic professionals with families",
    ],
    "5A3": [
        "Urbanites",
        "Urban professionals and families",
        "Families in terraces and flats",
    ],
    "5B1": ["Urbanites", "Ageing urban living", "Delayed retirement"],
    "5B2": ["Urbanites", "Ageing urban living", "Communal retirement"],
    "5B3": ["Urbanites", "Ageing urban living", "Self-sufficient retirement"],
    "6A1": ["Suburbanites", "Suburban achievers", "Indian tech achievers"],
    "6A2": ["Suburbanites", "Suburban achievers", "Comfortable suburbia"],
    "6A3": ["Suburbanites", "Suburban achievers", "Detached retirement living"],
    "6A4": ["Suburbanites", "Suburban achievers", "Ageing in suburbia"],
    "6B1": ["Suburbanites", "Semi-detached suburbia", "Multi-ethnic suburbia"],
    "6B2": ["Suburbanites", "Semi-detached suburbia", "White suburban communities"],
    "6B3": ["Suburbanites", "Semi-detached suburbia", "Semi-detached ageing"],
    "6B4": ["Suburbanites", "Semi-detached suburbia", "Older workers and retirement"],
    "7A1": [
        "Constrained city dwellers",
        "Challenged diversity",
        "Transitional Eastern European neighbourhood",
    ],
    "7A2": ["Constrained city dwellers", "Challenged diversity", "Hampered aspiration"],
    "7A3": [
        "Constrained city dwellers",
        "Challenged diversity",
        "Multi-ethnic hardship",
    ],
    "7B1": [
        "Constrained city dwellers",
        "Constrained flat dwellers",
        "Eastern European communities",
    ],
    "7B2": [
        "Constrained city dwellers",
        "Constrained flat dwellers",
        "Deprived neighbourhoods",
    ],
    "7B3": [
        "Constrained city dwellers",
        "Constrained flat dwellers",
        "Endeavouring flat dwellers",
    ],
    "7C1": [
        "Constrained city dwellers",
        "White communities",
        "Challenged transitionaries",
    ],
    "7C2": [
        "Constrained city dwellers",
        "White communities",
        "Constrained young families",
    ],
    "7C3": ["Constrained city dwellers", "White communities", "Outer city hardship"],
    "7D1": [
        "Constrained city dwellers",
        "Ageing city dwellers",
        "Ageing communities and families",
    ],
    "7D2": [
        "Constrained city dwellers",
        "Ageing city dwellers",
        "Retired independent city dwellers",
    ],
    "7D3": [
        "Constrained city dwellers",
        "Ageing city dwellers",
        "Retired communal city dwellers",
    ],
    "7D4": [
        "Constrained city dwellers",
        "Ageing city dwellers",
        "Retired city hardship",
    ],
    "8A1": [
        "Hard-pressed living",
        "Industrious communities",
        "Industrious transitions",
    ],
    "8A2": ["Hard-pressed living", "Industrious communities", "Industrious hardship"],
    "8B1": [
        "Hard-pressed living",
        "Challenged terraced workers",
        "Deprived blue-collar terraces",
    ],
    "8B2": [
        "Hard-pressed living",
        "Challenged terraced workers",
        "Hard pressed rented terraces",
    ],
    "8C1": [
        "Hard-pressed living",
        "Hard pressed ageing workers",
        "Ageing industrious workers",
    ],
    "8C2": [
        "Hard-pressed living",
        "Hard pressed ageing workers",
        "Ageing rural industry workers",
    ],
    "8C3": [
        "Hard-pressed living",
        "Hard pressed ageing workers",
        "Renting hard-pressed workers",
    ],
    "8D1": [
        "Hard-pressed living",
        "Migration and churn",
        "Young hard-pressed families",
    ],
    "8D2": ["Hard-pressed living", "Migration and churn", "Hard-pressed ethnic mix"],
    "8D3": [
        "Hard-pressed living",
        "Migration and churn",
        "Hard-Pressed European Settlers",
    ],
    "9Z9": ["(pseudo) CI, IoM", "(pseudo) CI, IoM", "(pseudo) CI, IoM"],
}

RU11IND_CODES = {
    "A1": "Urban major conurbation",
    "B1": "Urban minor conurbation",
    "C1": "Urban city and town",
    "C2": "Urban city and town in a sparse setting",
    "D1": "Rural town and fringe",
    "D2": "Rural town and fringe in a sparse setting",
    "E1": "Rural village",
    "E2": "Rural village in a sparse setting",
    "F1": "Rural hamlet and isolated dwellings",
    "F2": "Rural hamlet and isolated dwellings in a sparse setting",
    "1": "Large Urban Area",
    "2": "Other Urban Area",
    "3": "Accessible Small Town",
    "4": "Remote Small Town",
    "5": "Very Remote Small Town",
    "6": "Accessible Rural",
    "7": "Remote Rural",
    "8": "Very Remote Rural",
}


NHSPD_FIELDNAMES = [
    "pcd2",
    "pcds",
    "dointr",
    "doterm",
    "oseast100m",
    "osnrth100m",
    "oscty",
    "odslaua",
    "oslaua",
    "osward",
    "usertype",
    "osgrdind",
    "ctry",
    "oshlthau",
    "rgn",
    "oldha",
    "nhser",
    "sicbl",
    "psed",
    "cened",
    "edind",
    "ward98",
    "oa01",
    "nhsrlo",
    "hro",
    "lsoa01",
    "ur01ind",
    "msoa01",
    "cannet",
    "scn",
    "oshaprev",
    "oldpct",
    "oldhro",
    "pcon",
    "canreg",
    "pct",
    "oseast1m",
    "osnrth1m",
    "oa11",
    "lsoa11",
    "msoa11",
    "calncv",
    "icb",
    "smhpc_aed",
    "smhpc_as",
    "smhpc_ct4",
    "oa21",
    "lsoa21",
    "msoa21",
]
