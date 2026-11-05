import requests
import re
import json
from pathlib import Path

cache_file = Path("cache.json")

def load_data(opcao):
    if cache_file.exists():
        with cache_file.open(encoding="utf-8") as file:
            return json.load(file)
            
    url = f"https://wger.de/api/v2/{opcao}"
    params = {"limit": 20, "offset": 0}
    cache = {"count": 0, "results": []}
    while url:
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                page = response.json()
            except requests.exceptions.RequestException as error:
                print(f"Error consulting the dataset: {error}")
                return None
            cache["count"] = page["count"]
            cache["results"].extend(page["results"])
            url = page["next"]
            
    with cache_file.open("w", encoding="utf-8") as file:
        json.dump(cache, file, ensure_ascii=False, indent=2)
    return cache

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

cache = load_data("exerciseinfo")

if cache is None:
    raise SystemExit("Error loading data.")
