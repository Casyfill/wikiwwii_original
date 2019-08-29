from functools import lru_cache
from time import sleep

import pandas as pd
import requests

BASE_URL = "https://nominatim.openstreetmap.org/search?"


@lru_cache(maxsize=1000)
def nominatim_geocode(address, format="json", limit=1, **kwargs):
    """thin wrapper around nominatim API.
 
    Documentation: https://wiki.openstreetmap.org/wiki/Nominatim#Parameters
    """
    params = {"q": address, "format": format, "limit": limit, **kwargs}
    headers = {"Accept-Language": "en"}

    response = requests.get(BASE_URL, params=params, headers=headers)
    response.raise_for_status()  # will raise exception if status is unsuccessful

    sleep(1)  # sleep
    return response.json()


def extract_latlon(locColumn):
    """extracts latlon from the location"""
    latlon_pattern = r"/ ([\d|\.]+); ([\d|\.]+)"
    latlon = locColumn.str.extract(latlon_pattern)
    for col in range(2):
        latlon.iloc[:, col] = latlon.iloc[:, col].astype(float)

    return pd.DataFrame(latlon, columns=["lat", "lon"], index=locColumn.index)


LOC_REPLACEMENTS = {
    "Ukrainian SSR, Soviet Union": "Ukraine",
    "Russian SFSR, Soviet Union": "Russia",
    "Russian SFSR": "Russia",
    "Belorussian SSR": "Belorus",
    "Soviet Union": "",
    "USSR": "",
    ", Poland (now Ukraine)": "Ukraine",
    "east prussia (now kaliningrad oblast)": "Kaliningrad Oblast, Russia",
    ", czechoslovakia": ", czech republic",
    "königsberg, germany (now: kaliningrad, russia)": "Kaliningrad Oblast, Russia",
    "lwów, lwów voivodeship, poland": "Lvov, Ukraine",
    "leningrad region, ; narva, estonia": "Narva, Estonia",
    "Kingdom of Hungary": "Hungary",
    "odessa region, ukraine": "Odessa, Ukraine",
}


def geocode_location(locColumn, replacements=LOC_REPLACEMENTS, errata=None):
    """attempts to geocode locations.
    don't forget to use mask not to waste 
    geocoding on those located already"""

    location = locColumn.str.lower().str.replace("near ", "")

    if replacements is not None:
        for k, v in replacements.items():
            location = location.str.replace(k.lower(), v.lower(), regex=False)
    if errata is not None:
        for k, v in errata.items():
            location = location.replace(k.lower(), v.lower(), regex=False)

    def _vectorized_geocode(x):
        result = nominatim_geocode(x)
        if len(result) == 0:
            return dict()
        return {k: result[0][k] for k in ("lat", "lon", "importance", "display_name")}

    result = location.str.replace("\n", " ").progress_apply(_vectorized_geocode)
    return pd.DataFrame(result.tolist(), index=locColumn.index)


def process_locations(locColumn, replacements=None, errata=None):
    """wrapper for all location processies
    - both extaction and geolocation"""
    loc = extract_latlon(locColumn)

    mask = loc.iloc[:, 0].isnull()

    loc2 = geocode_location(locColumn[mask], replacements=replacements, errata=errata)

    # combine, ensuring consistent order and indexing
    combined_result = pd.concat([loc2, loc[mask]], axis=0).reindex(locColumn.index)
    return combined_result
