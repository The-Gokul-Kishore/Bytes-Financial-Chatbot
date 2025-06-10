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

@app.command()
def backend(
    port: int = typer.Option(8021, "--port", "-p", help="Port number"),
    reload: bool = typer.Option(True, "--reload", "-r", help="Reload"),
):
    from bytes.backend import run_backend

    try:
        console.print("[bold green]Starting backend[/]")
        run_backend(port=port, reload=reload)
        console.print("[bold green]Backend stopped[/]")
    except Exception as e:
        console.print("[red]Backend stopped with error:[/red]", e)


@app.command()
def init_setup():
    from bytes.database.db import DBManager

    db_manager = DBManager()
    db_manager.init_db()
    console.print("[green]Database initialized[/green]")
    from bytes.database.crud.ClientManager import ClientManager

    with db_manager.session() as db:
        client_manager = ClientManager()
        client_manager.create_client(username="bot", email="bot", password="bot", db=db)
        console.print("[green]Client created[/green]")
        client_manager.create_client(
            username="user", email="user", password="user", db=db
        )


@app.command()
def create_a_thread(
    thread_name: str = typer.Option(..., "--thread-name", "-n", help="Thread name"),
    thread_type: str = typer.Option(..., "--thread-type", "-t", help="Thread type"),
):
    from bytes.database.crud.ThreadManager import ThreadManager
    from bytes.database.db import DBManager

    db_manager = DBManager()
    with db_manager.session() as db:
        thread_manager = ThreadManager()
        thread_manager.create_thread_by_username(
            username="user", thread_type=thread_type, db=db
        )
        console.print(f"[green]Thread {thread_name} created[/green]")

