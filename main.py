import requests
import re
import json
from pathlib import Path

def load_data(opcao):
    cache_file = Path(f"cache_{opcao}.json")
    if cache_file.exists():
        with cache_file.open(encoding="utf-8") as file:
            return json.load(file)
            
    url = f"https://wger.de/api/v2/{opcao}"
    params = {"limit": 100, "offset": 0}
    cache = {"count": 0, "results": []}
    while url:
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                page = response.json()
            except requests.exceptions.RequestException as error:
                print(f"Error consulting the dataset: {error}")
                return None
            for ex in page["results"]:
                english = [t for t in ex["translations"] if t["language"]==2]
                if english:
                    cache["results"].append({**ex, "translations": english})
            
            url = page["next"]
            params = None
            cache["count"] = len(cache["results"])
            
    with cache_file.open("w", encoding="utf-8") as file:
        json.dump(cache, file, ensure_ascii=False, indent=2)
    return cache

def list_n(n):
    return [{"name": ex["translations"][0]["name"],
             "category": ex["category"]["name"],
             "equipment": [e["name"] for e in ex["equipment"]]}
            for ex in cache["results"][-n:]]

def search_musc_cat_list(term, n):
    result = []
    for ex in cache["results"]:
        muscles = [m["name_en"] or m["name"] for m in ex["muscles"]]
        text = ex["category"]["name"] + " " + " ".join(muscles)
        if term.lower() in text.lower():
            result.append({"name": ex["translations"][0]["name"],
                           "category": ex["category"]["name"],
                           "equipment": [e["name"] for e in ex["equipment"]]})
    return result[:n]

def extract_type_id(exercise_id):

    return None

def count_equipment(category):
    equipment = ["barbell", "dumbbell", "cable", "machine", "bodyweight"]
    pairs_count = []
    for word in equipment:
        total = 0
        for ex in cache["results"]:
            if category.lower() in ex["category"]["name"].lower():
                text = ex["translations"][0]["description"].lower()
                eq_found = re.findall(word, text)
                total = total + len(eq_found)
        pairs_count.append([total, word])
    pairs_count.sort(reverse = True)
    result = []
    for pair in pairs_count:
        result.append({pair[1]: pair[0]})
    return result

def personal_workout(terms, effor, n):
    return

def export_csv(plan, path):
    return

cache = load_data("exerciseinfo")

if cache is None:
    raise SystemExit("Error loading data.")
