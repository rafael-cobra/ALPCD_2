import requests
import re
import json
from pathlib import Path

cache_file = Path("cache.json")

def load_data(opcao):
    if cache_file.exists():
        with cache_file.open(encoding="utf-8") as file:
            cache = json.load(file)
    else:
        api = f"https://wger.de/api/v2/{opcao}"
        params = {"limit": 186, "offset": 0}
        cache = {"count": 0, "results": []}
        while params["offset"] < cache["count"] or params["offset"] == 0:
            try:
                response = requests.get(api, params=params)
                response.raise_for_status()
                page = response.json()
                cache["count"] = page["count"]
                cache["results"].extend(page["results"])
                params["offset"] += params["limit"]
            except requests.exceptions.RequestException as error:
                print(f"Error consulting the dataset: {error}")
        with cache_file.open("w", encoding="utf-8") as file:
            json.dump(cache, file, ensure_ascii=False, indent=2)

load_data(opcao = "exerciseinfo")

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

