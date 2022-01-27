import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

# postcode data URLs
NSPL_URL = "https://www.arcgis.com/sharing/rest/content/items/677cfc3ef56541999314efc795664ce9/data"
ONSPD_URL = "https://www.arcgis.com/sharing/rest/content/items/a644dd04d18f4592b7d36705f93270d8/data"
