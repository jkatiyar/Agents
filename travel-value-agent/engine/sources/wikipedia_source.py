# engine/sources/wikipedia_source.py

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta


WIKI_BASE = "https://en.wikipedia.org/wiki/"


def fetch_place_facts(place_name: str):
    """
    Fetch altitude, languages, and population context dynamically from Wikipedia.
    """
    url = WIKI_BASE + place_name.replace(" ", "_")
    resp = requests.get(url, timeout=15)

    if resp.status_code != 200:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    info = {
        "altitude_m": None,
        "languages": [],
        "population_context": "Unknown",
        "fetched_at": datetime.utcnow().isoformat()
    }

    infobox = soup.find("table", class_="infobox")
    if not infobox:
        return info

    for row in infobox.find_all("tr"):
        header = row.find("th")
        value = row.find("td")

        if not header or not value:
            continue

        h = header.text.lower()
        v = value.text.strip()

        # Altitude
        if "elevation" in h or "altitude" in h:
            m = re.search(r"(\d+)\s*m", v)
            if m:
                info["altitude_m"] = int(m.group(1))

        # Languages
        if "languages" in h:
            langs = re.split(r",|\n", v)
            info["languages"] = [l.strip() for l in langs if l.strip()]

        # Population proxy
        if "population" in h:
            num = re.search(r"([\d,]+)", v)
            if num:
                n = int(num.group(1).replace(",", ""))
                if n > 1_000_000:
                    info["population_context"] = "High"
                elif n > 200_000:
                    info["population_context"] = "Medium"
                else:
                    info["population_context"] = "Low"

    return info
