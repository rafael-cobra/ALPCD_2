import requests
import re
import json
from pathlib import Path


def load_data(option):
    cache_file = Path(f"cache_{option}.json")
    if cache_file.exists():
        with cache_file.open(encoding="utf-8") as file:
            return json.load(file)

    url = f"https://wger.de/api/v2/{option}"
    headers = {"User-Agent": "fitcli-ALPCD2/1.0 (Projeto Grupo 2, Universidade do Minho)"}
    params = {"limit": 100, "offset": 0}
    cache = {"count": 0, "results": []}
    while url:
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            page = response.json()
        except requests.exceptions.RequestException as error:
            print(f"Error consulting the dataset: {error}")
            return None

        for exercise_entry in page["results"]:
            english_translations = [
                translation
                for translation in exercise_entry["translations"]
                if translation["language"] == 2
            ]
            if english_translations:
                cache["results"].append({**exercise_entry, "translations": english_translations})

        url = page["next"]
        params = None
        cache["count"] = len(cache["results"])

    with cache_file.open("w", encoding="utf-8") as file:
        json.dump(cache, file, ensure_ascii=False, indent=2)
    return cache


def find_exercise(exercise_id):
    # Search first by exercise ID
    for exercise in cache["results"]:
        if exercise["id"] == exercise_id:
            return exercise

    # If not found, search by translation ID
    for exercise in cache["results"]:
        if any(
            translation["id"] == exercise_id
            for translation in exercise.get("translations", [])
        ):
            return exercise

    return None

def summarize(exercise):
    return {
        "id": exercise["id"],
        "name": exercise["translations"][0]["name"],
        "category": exercise["category"]["name"],
        "muscles": [m["name"] for m in exercise.get("muscles", [])],
        "muscles_secondary": [m["name"] for m in exercise.get("muscles_secondary", [])],
        "equipment": [e["name"] for e in exercise["equipment"]],
    }

def list_last_n(n):
    return [summarize(exercise) for exercise in cache["results"][-n:]]

def search_exercises(term, limit):
    term = term.lower()
    matches = []

    for exercise in cache["results"]:
        muscle_hit = any(term in muscle.lower() for muscle in get_muscle_names(exercise))
        category_hit = exercise.get("category", {}).get("name", "").lower() == term

        if muscle_hit or category_hit:
            matches.append(summarize(exercise))
            if len(matches) == limit:
                break

    return matches

def is_cardio(name, description, category):
    name = name.lower()
    description = description.lower()
    category = (category or "").lower()

    name_pattern = r"\b(running|run|cycling|jogging|swimming|treadmill|jump rope|rowing machine)\b"
    description_pattern = r"\b(cycling|jogging|swimming|treadmill|jump rope)\b"
    effort_pattern = r"\b(aerobic|endurance|cardiovascular|heart rate|as fast as you can|for \d+ minutes|short breaks?)\b"

    clear_cardio_activity = (
        re.search(name_pattern, name)
        or re.search(description_pattern, description)
    )

    category_with_effort = (
        category == "cardio"
        and re.search(effort_pattern, description)
    )

    return bool(clear_cardio_activity or category_with_effort)

def get_muscle_names(exercise):
    muscles = exercise.get("muscles", [])
    secondary_muscles = exercise.get("muscles_secondary", [])

    names = []

    for muscle in muscles + secondary_muscles:
        names.append(muscle["name"])

    return names


def count_muscles(exercise):
    muscles = get_muscle_names(exercise)

    return len(muscles)


def has_muscle_support(exercise):
    muscles = get_muscle_names(exercise)

    return len(muscles) >= 2


def is_isolated(name, description):
    text = f"{name} {description}".lower()

    pattern = r"\b(curls?|leg extensions?|knee extensions?|triceps extensions?|lateral raises?|fly|shrugs?|calf raises?)\b"

    return bool(re.search(pattern, text))


def is_compound(name, description, exercise):
    if is_isolated(name, description):
        return False

    if not has_muscle_support(exercise):
        return False

    # Recognized compound movements by name
    name_pattern = r"\b(deadlift|bench press|pull-up|push-up|lunge|row|rowing)\b"

    # Evidence of movement across multiple joints
    movement_pattern = r"\b(knees and hips|hips and knees)\b"

    return bool(
        re.search(name_pattern, name)
        or re.search(movement_pattern, description)
    )


def extract_type_id(exercise_id):
    exercise = find_exercise(exercise_id)

    if exercise is None:
        return "other"

    translation = exercise["translations"][0]

    name = translation["name"].lower()
    description = translation["description"].lower()
    category = exercise.get("category", {}).get("name", "").lower()

    if is_cardio(name, description, category):
        return "cardio"

    if is_isolated(name, description):
        return "isolated"

    if is_compound(name, description, exercise):
        return "compound"

    return "other"


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


def personal_workout(terms, effort, n):
    return


def export_csv(plan, path):
    return


cache = load_data("exerciseinfo")

if cache is None:
    raise SystemExit("Error loading data.")