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

def find_exercise(exercise_id):
    # Procurar primeiro pelo ID do exercício
    for exercise in cache["results"]:
        if exercise["id"] == exercise_id:
            return exercise

   # Se não encontrar, procurar pelo ID da tradução
    for exercise in cache["results"]:
        if any(
            translation["id"] == exercise_id
            for translation in exercise.get("translations", [])
        ):
            return exercise

    return None

def list_n(n):
    return [{"name": ex["translations"][0]["name"],
             "category": ex["category"]["name"],
             "equipment": [e["name"] for e in ex["equipment"]]}
            for ex in cache["results"][-n:]]

def search_musc_cat_list(valor, tipo):
    encontrados = []

    for exercise in cache["results"]:

        if tipo == "muscle":
            muscles = get_muscle_names(exercise)

            if any(valor.lower() in muscle.lower() for muscle in muscles):
                encontrados.append(exercise)

        elif tipo == "category":
            category = exercise.get("category", {})

            if category.get("name", "").lower() == valor.lower():
                encontrados.append(exercise)

    return encontrados

def is_cardio(name, description):
    name = name.lower()
    description = description.lower()

    padrao_nome = r"\b(running|run|cycling|jogging|swimming|treadmill|jump rope|rowing machine)\b"
    padrao_descricao = r"\b(cycling|jogging|swimming|treadmill|jump rope)\b"

    return bool(
        re.search(padrao_nome, name)
        or re.search(padrao_descricao, description)
    )

def get_muscle_names(exercise):
    muscles = exercise.get("muscles", [])
    secondary = exercise.get("muscles_secondary", [])

    names = []

    for muscle in muscles + secondary:
        names.append(muscle["name"])

    return names

def count_muscles(exercise):
    muscles = get_muscle_names(exercise)

    return len(muscles)

def has_muscle_support(exercise):
    muscles = get_muscle_names(exercise)

    return len(muscles) >= 2

def is_isolated(name, description):
    texto = f"{name} {description}".lower()

    padrao = r"\b(curls?|leg extensions?|knee extensions?|triceps extensions?|lateral raises?|fly|shrugs?|calf raises?)\b"

    return bool(re.search(padrao, texto))

def is_compound(name, description, exercise):

    if is_isolated(name, description):
        return False

    if not has_muscle_support(exercise):
        return False

    # Movimentos compostos reconhecidos pelo nome
    padrao_nome = r"\b(deadlift|bench press|pull-up|push-up|lunge|row|rowing)\b"

    # Evidências de movimento em várias articulações
    padrao_movimento = r"\b(knees and hips|hips and knees)\b"

    return bool(
        re.search(padrao_nome, name)
        or re.search(padrao_movimento, description)
    )

def extract_type_id(exercise_id):
    exercise = find_exercise(exercise_id)

    if exercise is None:
        return "other"

    translation = exercise["translations"][0]

    name = translation["name"].lower()
    description = translation["description"].lower()

    if is_cardio(name, description):
        return "cardio"

    if is_isolated(name, description):
        return "isolated"

    if is_compound(name, description, exercise):
        return "compound"

    return "other"

def count_equipment(category):
    return

def personal_workout(terms, effor, n):
    return

def export_csv(plan, path):
    return

cache = load_data("exerciseinfo")

if cache is None:
    raise SystemExit("Error loading data.")
