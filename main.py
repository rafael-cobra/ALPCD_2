import csv
import json
import re
from pathlib import Path
import requests
import os

BASE_URL = "https://wger.de/api/v2"
LANGUAGE_EN = 2
HEADERS = {"User-Agent": "fitcli-ALPCD2/1.0 (Projeto Grupo 2, Universidade do Minho)"}
EQUIPMENT_WORDS = ["barbell", "dumbbell", "cable", "machine", "bodyweight"]

CARDIO_NAME_RE = re.compile(r"\b(running|run|cycling|jogging|swimming|treadmill|jump rope|rowing machine)\b")
CARDIO_DESC_RE = re.compile(r"\b(cycling|jogging|swimming|treadmill|jump rope)\b")
CARDIO_EFFORT_RE = re.compile(r"\b(aerobic|endurance|cardiovascular|heart rate|as fast as you can|for \d+ minutes|short breaks?)\b")
ISOLATED_RE = re.compile(r"\b(curls?|hammer[ -]?curls?|leg extensions?|knee extensions?|triceps extensions?|lateral raises?|front raises?|"
    r"butterfly|butterflies|fly|flyes|shrugs?|calf raises?|hip adductions?)\b")
COMPOUND_NAME_RE = re.compile(r"\b(deadlifts?|bench[-\s]?press|presses|press|pull[-\s]?ups?|chin[-\s]?ups?|push[-\s]?ups?|"
    r"lunges?|squats?|dips?|rows?|rowing|kettlebell swings?)\b")
COMPOUND_MOVE_RE = re.compile(r"\b(knees and hips|hips and knees)\b")

def clean(text):
    """Tira as tags HTML e os espaços a mais de um texto e passa tudo para minúsculas."""
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()

def load_data(option):
    """Descarrega todas as páginas da API para a rota indicada (só em inglês) e guarda em cache JSON.
    Se o ficheiro de cache já existir, lê-o em vez de chamar a API. Devolve None se o pedido falhar."""
    cache_file = Path(f"cache_{option}.json")
    if cache_file.exists():
        with cache_file.open(encoding="utf-8") as file:
            return json.load(file)

    url = f"{BASE_URL}/{option}"
    params = {"limit": 100, "offset": 0, "language": LANGUAGE_EN}
    cache = {"count": 0, "results": []}

    with requests.Session() as session:
        session.headers.update(HEADERS)
        while url:
            try:
                response = session.get(url, params=params, timeout=30)
                response.raise_for_status()
                page = response.json()
            except requests.exceptions.RequestException as error:
                print(f"Error consulting the dataset: {error}")
                return None

            for entry in page["results"]:
                english = [t for t in entry["translations"] if t["language"] == LANGUAGE_EN]
                if english:
                    cache["results"].append({**entry, "translations": english})

            url = page["next"]
            params = None

    cache["count"] = len(cache["results"])
    with cache_file.open("w", encoding="utf-8") as file:
        json.dump(cache, file, ensure_ascii=False, indent=2)
    return cache

def find_exercise(exercise_id):
    """Procura um exercício pelo id. Devolve None se não existir."""
    for exercise in cache["results"]:
        if exercise["id"] == exercise_id:
            return exercise

    return None

def summarize(exercise):
    """Devolve só os campos que interessam (id, nome, categoria, músculos, equipamento e tipo)."""
    return {
        "id": exercise["id"],
        "name": exercise["translations"][0]["name"],
        "category": exercise["category"]["name"],
        "muscles": [m["name"] for m in exercise.get("muscles", [])],
        "muscles_secondary": [m["name"] for m in exercise.get("muscles_secondary", [])],
        "equipment": [e["name"] for e in exercise["equipment"]],
        "type": classify(exercise),
    }

def list_last_n(n):
    """Devolve os n exercícios mais recentes (os últimos da lista)."""
    if n < 1:
        raise ValueError("n must be at least 1")
    return [summarize(exercise) for exercise in cache["results"][-n:]]

def get_muscle_names(exercise):
    """Devolve os nomes de todos os músculos do exercício, principais e secundários."""
    muscles = exercise.get("muscles", []) + exercise.get("muscles_secondary", [])
    return [muscle["name"] for muscle in muscles]

def matches(exercise, term):
    """Diz se o termo aparece no nome de algum músculo ou na categoria do exercício."""
    term = term.lower()
    return (
        any(term in muscle.lower() for muscle in get_muscle_names(exercise))
        or term in exercise["category"]["name"].lower()
    )

def search_exercises(term, limit=None):
    """Pesquisa por músculo ou categoria, opcionalmente limitada a N resultados."""
    if limit is not None and limit < 1:
        raise ValueError("limit must be at least 1")

    results = []
    for exercise in cache["results"]:
        if matches(exercise, term):
            results.append(summarize(exercise))
            if limit is not None and len(results) >= limit:
                break
    return results

def is_cardio(name, description, category):
    """Verifica com regex se o exercício é de cardio, pelo nome, descrição ou categoria."""
    return bool(
        CARDIO_NAME_RE.search(name)
        or CARDIO_DESC_RE.search(description)
        or (category == "cardio" and CARDIO_EFFORT_RE.search(description))
    )

def is_isolated(name, description):
    """Verifica com regex se o exercício é isolado (curl, extension, lateral raise...)."""
    return bool(ISOLATED_RE.search(f"{name} {description}"))

def is_compound(name, description, exercise):
    """Classifica como composto com uma pista de movimento ou nome reconhecido.
    O número de músculos só apoia uma pista de movimento; não basta sozinho.
    """
    if is_isolated(name, description):
        return False

    has_compound_name = bool(COMPOUND_NAME_RE.search(name))
    has_compound_movement = bool(COMPOUND_MOVE_RE.search(description))
    has_multiple_muscles = len(get_muscle_names(exercise)) >= 2

    return has_compound_name or (has_compound_movement and has_multiple_muscles)

def classify(exercise):
    """Devolve cardio, isolated, compound ou other, por esta ordem de prioridade."""
    translation = exercise["translations"][0]
    name = translation["name"].lower()
    description = clean(translation["description"])
    category = exercise["category"]["name"].lower()

    if is_cardio(name, description, category):
        return "cardio"
    if is_isolated(name, description):
        return "isolated"
    if is_compound(name, description, exercise):
        return "compound"
    return "other"

def extract_type_id(exercise_id):
    """Devolve o tipo de esforço do exercício com esse id, ou None se não existir."""
    exercise = find_exercise(exercise_id)
    return classify(exercise) if exercise else None

def count_equipment(category):
    """count_equipent conta quantas vezes aparece cada equipamento nas descrições dos exercicios, de uma certa categoria, devolvendo o resultado ordenado de forma decrescente
    em suma, mostra qual é o equipamento que aparece mais vezes numa categoria, por ordem descrescente """
    pairs = []
    for word in EQUIPMENT_WORDS:
        total = 0
        for ex in cache["results"]:
            if category.lower() in ex["category"]["name"].lower():
                text = clean(ex["translations"][0]["description"])
                total += text.count(word)
        pairs.append([total, word])

    pairs.sort(reverse=True)

    result = []
    for pair in pairs:
        result.append({pair[1]: pair[0]})
    return result

def available():
    """Devolve categorias, músculos, equipamentos e tipos disponíveis."""
    return {
        "categories": sorted({
            ex["category"]["name"]
            for ex in cache["results"]
        }),
        "muscles": sorted({
            muscle
            for ex in cache["results"]
            for muscle in get_muscle_names(ex)
        }),
        "equipment": sorted({
            item["name"]
            for ex in cache["results"]
            for item in ex["equipment"]
        }),
        "types": ["cardio", "isolated", "compound", "other"],
    }

def personal_workout(terms, effort, n):
    """Cria o plano de treino: para cada músculo ou categoria, filtra pelo tipo de esforço
    (ou não filtra se for 'any') e guarda os primeiros n exercícios."""
    if n < 1:
        raise ValueError("n must be at least 1")

    workout = {}
    for term in terms:
        term = term.strip()
        exercises = search_exercises(term)
        if effort != "any":
            exercises = [ex for ex in exercises if ex["type"] == effort]
        workout[term] = exercises[:n]
    return workout

def export_csv(plan, path):
    """Escreve o plano num ficheiro CSV e devolve o número de registos exportados."""
    rows = [
        {**ex, "group": group,
         "muscles": ", ".join(ex["muscles"]),
         "equipment": ", ".join(ex["equipment"])}
        for group, exercises in plan.items()
        for ex in exercises
    ]
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["group", "name", "category", "type", "muscles", "equipment"],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)

def load_routines():
    """Vai buscar as routines públicas da wger (precisa de WGER_TOKEN) e guarda em cache.
    Para cada routine guarda o nome e os ids dos exercícios de cada dia."""
    cache_file = Path("cache_routines.json")
    if cache_file.exists():
        with cache_file.open(encoding="utf-8") as file:
            return json.load(file)

    token = os.environ.get("WGER_TOKEN")
    if not token:
        print("Set the WGER_TOKEN environment variable first.")
        return None

    headers = {**HEADERS, "Authorization": f"Token {token}"}
    routines = {}
    url = f"{BASE_URL}/routine/"
    params = {"limit": 100, "is_template": "true", "is_public": "true"}

    try:
        while url:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            page = response.json()
            for routine in page["results"]:
                response = requests.get(f"{BASE_URL}/routine/{routine['id']}/structure/",
                                        headers=headers, timeout=30)
                response.raise_for_status()
                days = [
                    [entry["exercise"] for slot in day["slots"] for entry in slot["entries"]]
                    for day in response.json()["days"]
                ]
                routines[str(routine["id"])] = {"name": routine["name"], "days": days}
            url = page["next"]
            params = None
    except requests.exceptions.RequestException as error:
        print(f"Error consulting the routines: {error}")
        return None

    with cache_file.open("w", encoding="utf-8") as file:
        json.dump(routines, file, ensure_ascii=False, indent=2)
    return routines

def exercise_name(exercise_id):
    """Devolve o nome do exercício, ou o próprio id se não o encontrar."""
    exercise = find_exercise(exercise_id)
    return exercise["translations"][0]["name"] if exercise else str(exercise_id)

routine_cache = None

def get_routine_cache():
    global routine_cache

    if routine_cache is None:
        routine_cache = load_routines()

    if routine_cache is None:
        raise SystemExit("Could not load routines. Check WGER_TOKEN and the API.")

    return routine_cache

def routines_for_exercise(exercise_id):
    """Devolve as rotinas que têm este exercício em algum dos dias."""
    routines = get_routine_cache()
    return [
        {"id": int(rid), "name": routine["name"]}
        for rid, routine in routines.items()
        if any(exercise_id in day for day in routine["days"])
    ]
    
def get_routine(routine_id):
    """Devolve o nome da rotina e os exercícios de cada dia, ou None se não existir."""
    routines = get_routine_cache()
    routine = routines.get(str(routine_id))
    if routine is None:
        return None
    return {
        "name": routine["name"],
        "days": [[exercise_name(i) for i in day] for day in routine["days"]],
    }

cache = load_data("exerciseinfo")

if cache is None:
    raise SystemExit("Error loading exercise data.")