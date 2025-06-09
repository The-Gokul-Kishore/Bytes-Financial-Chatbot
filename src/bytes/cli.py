from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console

console = Console()
app = typer.Typer(name="bytes", help="bytes cli")



@app.callback()
def load_env(
    env: Path = typer.Option(
        Path(".env"), "--env", "-e", help="Environment config file"
    ),
):
    if not env.exists():
        console.print("[red]Environment config file not found[/red]")
        return
    load_dotenv(dotenv_path=env, override=True)
    console.print("[green]Environment config file loaded[/green]")


@app.command()
def delete_db():
    from bytes.database.db import DBManager

    db_manager = DBManager()
    db_manager.drop_all()
    console.print("[green]Database deleted[/green]")


@app.command()
def init_db():
    from bytes.database.db import DBManager

    db_manager = DBManager()
    db_manager.init_db()
    console.print("[green]Database initialized[/green]")
