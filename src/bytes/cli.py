from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from bytes.database.db import DBManager
console = Console()
app = typer.Typer(name="bytes", help="bytes cli")


db_manager = DBManager()
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
@app.command()
def run_agent(
    query: str = typer.Option(..., "--query", "-q", help="Query"),
    thread_id: int = typer.Option(1, "--thread-id", "-t", help="Thread id"),
):
    try:
        from bytes.agent_services.agent import Agent_Service
        with db_manager.session() as session:
            agent = Agent_Service(model="gemini-1.5-flash",db_manager=session)
            agent.run_agent(query=query, thread_id=thread_id,db=session,thread_specific_call=False)
    except Exception as e:
        console.print("[red]Agent stopped with error:[/red]", e)
@app.command()
def delete_vecst():
    from bytes.retriver.retriver import Retriver

    parser = Retriver()
    parser.delete_vectorstore()
    console.print("[green]vectore Stores deleted[/green]")