import requests
import re
import json
from pathlib import Path

api = "https://wger.de/api/v2/"
cache_file = Path("cache.json")

def load_data():
    if cache_file.exists():
        with cache_file.open(encoding="utf-8") as file:
            cache = json.load(file)
    else:
        api = "https://wger.de/api/v2/"
        params = {"limit": 0, "offset": 0}
        cache = {"total_count": 0, "results": []}
        while params["offset"] < cache["total_count"] or params["offset"] == 0:
            try:
                response = requests.get(api, params=params)
                response.raise_for_status()
                page = response.json()
                cache["total_count"] = page["total_count"]
                cache["results"].extend(page["results"])
                params["offset"] += params["limit"]
            except requests.exceptions.RequestException as error:
                print(f"Error consulting the dataset: {error}")
        with cache_file.open("w", encoding="utf-8") as file:
            json.dump(cache, file, ensure_ascii=False, indent=2)
            
def list_n_ex():
    return

def search_musc_cat_list():
    return

def extract_type_id():
    return

def count_equipment():
    return

def personal_workout():
    return