import typer
import json
import main

app = typer.Typer()

def show(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))

@app.command()
def top(n: int):
    show(main.list_n(n))
    
@app.command()
def search(term: str, n: int):
    show(main.search_musc_cat_list(term, n))
    
@app.command("type")
def type_(exercise_id:int):
    print(main.extract_type_id(exercise_id))
    
@app.command()
def equipment(category: str):
    show(main.count_equipment(category))
    
@app.command()
def workout(muscles: str, effort: str, n: int, csv: str=None):
    if effort not in ("compound", "isolated", "any"):
        raise typer.BadParameter("effort must be compound, isolated or any")
    plan = main.personal_workout(muscles.split(","), effort, n)
    if csv:
        print(f"File exported: {csv} ({main.export_csv(plan, csv)} records)")
    else:
        show(plan)
        
if __name__ == "__main__":
    app()