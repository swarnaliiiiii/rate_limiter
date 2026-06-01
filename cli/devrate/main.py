import typer
from devrate.commands.check import check_command
from devrate.commands.trace import trace_command

app = typer.Typer(help="Devrate CLI")

app.command("check")(check_command)
app.command("trace")(trace_command)

def main():
    app()

if __name__ == "__main__":
    main()
