import typer
import json
import main

app = typer.Typer(no_args_is_help=True)

def show(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))

@app.command()
def search(term: str, n: int = typer.Argument(..., min=1)):
    """Pesquisa exercícios por músculo ou categoria e limita os resultados."""
    show(main.search_exercises(term, n))

@app.command()
def top(n: int = typer.Argument(..., min=1)):
    """Lista os N exercícios mais recentes."""
    show(main.list_last_n(n))

@app.command("type")
def type_(exercise_id: int):
    """Mostra o tipo de esforço de um exercício pelo seu ID."""
    result = main.extract_type_id(exercise_id)
    if result is None:
        typer.echo(f"Exercise {exercise_id} not found", err=True)
        raise typer.Exit(1)
    print(result)

@app.command()
def info(exercise_id: int):
    """Mostra os detalhes de um exercício."""
    result = main.exercise_info(exercise_id)
    if result is None:
        typer.echo(f"Exercise {exercise_id} not found", err=True)
        raise typer.Exit(1)
    show(result)

@app.command()
def equipment(category: str):
    """Conta menções a equipamento nas descrições de uma categoria."""
    show(main.count_equipment(category))
    
@app.command()
def workout(
    muscles: str,
    effort: str,
    n: int = typer.Argument(..., min=1),
    csv: str = None,
    equipment: str = None,
):
    """Cria um plano de treino, opcionalmente filtrado por equipamento."""
    if effort not in ("compound", "isolated", "any"):
        raise typer.BadParameter("effort must be compound, isolated or any")

    plan = main.personal_workout(
        muscles.split(","),
        effort,
        n,
        equipment=equipment,
    )

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
    """Lista rotinas públicas modelo que incluem o exercício indicado."""
    result = main.routines_for_exercise(exercise_id)
    if not result:
        typer.echo(f"No routines use exercise {exercise_id}", err=True)
        raise typer.Exit(1)
    show(result)

@app.command()
def routine(routine_id: int):
    """Mostra uma rotina e os exercícios de cada dia."""
    result = main.get_routine(routine_id)
    if result is None:
        typer.echo(f"Routine {routine_id} not found", err=True)
        raise typer.Exit(1)
    show(result)
    
@app.command()
def available():
    """Lista categorias, músculos, equipamentos e tipos disponíveis."""
    show(main.available())
    
if __name__ == "__main__":
    app()