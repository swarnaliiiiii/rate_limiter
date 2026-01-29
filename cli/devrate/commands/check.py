import typer
from rich.console import Console
from rich.table import Table

from devrate.api import DevrateAPI

console = Console()

def check_command(
    tenant: str = typer.Option(..., "--tenant", help="Tenant ID"),
    route: str = typer.Option(..., "--route", help="API route"),
    method: str = typer.Option(..., "--method", help="HTTP method"),
    user: str = typer.Option(None, "--user", help="User ID"),
    base_url: str = typer.Option(
        "http://localhost:8000",
        "--base-url",
        help="Devrate API base URL",
    ),
):
    api = DevrateAPI(base_url)

    payload = {
        "tenant_id": tenant,
        "route": route,
        "method": method,
        "user_id": user,
    }

    try:
        result = api.check_decision(payload)
    except Exception as e:
        console.print(f"[red]API Error:[/red] {e}")
        raise typer.Exit(1)

    table = Table(title="Devrate Decision")

    table.add_column("Field", style="bold")
    table.add_column("Value")

    table.add_row("Action", result["action"])
    table.add_row("Reason", result["reason"])
    table.add_row("Triggered By", result["triggered_by"])

    if result.get("retry_after") is not None:
        table.add_row("Retry After", f"{result['retry_after']}s")

    console.print(table)
