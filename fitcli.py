import typer
import json
import main

app = typer.Typer()

def show(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))

@app.command()
def search(term: str, n: int = typer.Argument(..., min=1)):
    show(main.search_exercises(term, n))

@app.command()
def top(n: int = typer.Argument(..., min=1)):
    show(main.list_last_n(n))

@app.command("type")
def type_(exercise_id: int):
    result = main.extract_type_id(exercise_id)
    if result is None:
        typer.echo(f"Exercise {exercise_id} not found", err=True)
        raise typer.Exit(1)
    print(result)
    
@app.command()
def equipment(category: str):
    show(main.count_equipment(category))
    
@app.command()
def workout(muscles: str, effort: str, n: int = typer.Argument(..., min=1),
            csv: str = None):
    if effort not in ("compound", "isolated", "any"):
        raise typer.BadParameter("effort must be compound, isolated or any")
    plan = main.personal_workout(muscles.split(","), effort, n)
    if not csv:
        show(plan)
        return
    try:
        count = main.export_csv(plan, csv)
    except OSError as error:
        typer.echo(f"Could not write {csv}: {error}", err=True)
        raise typer.Exit(1)
    print(f"File exported: {csv} ({count} records)")
        
@app.command()
def routines(exercise_id: int):
    result = main.routines_for_exercise(exercise_id)
    if not result:
        typer.echo(f"No routines use exercise {exercise_id}", err=True)
        raise typer.Exit(1)
    show(result)

@app.command()
def routine(routine_id: int):
    result = main.get_routine(routine_id)
    if result is None:
        typer.echo(f"Routine {routine_id} not found", err=True)
        raise typer.Exit(1)
    show(result)
    
if __name__ == "__main__":
    app()