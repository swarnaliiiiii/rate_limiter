import typer
from devrate.commands.check import check_command

app = typer.Typer(help="Devrate – Distributed Rate Limiting CLI")

app.command("check")(check_command)

def main():
    app()

if __name__ == "__main__":
    main()
