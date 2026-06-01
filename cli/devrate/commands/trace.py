import sys
import typer
from rich.console import Console

from devrate.api import DevrateAPI

console = Console()


def _supports_unicode() -> bool:
    """Legacy Windows consoles (cp1252) can't encode our glyphs — detect that
    and fall back to ASCII so the command never crashes on encode."""
    enc = getattr(sys.stdout, "encoding", None) or ""
    try:
        "✔⚠✖·".encode(enc)
        return True
    except (UnicodeEncodeError, LookupError):
        return False


_UNICODE = _supports_unicode()
_PASS = "✔" if _UNICODE else "OK"
_FAIL = "✖" if _UNICODE else "X"
_WARN = "⚠" if _UNICODE else "!"
_SKIP = "·" if _UNICODE else "-"

# Map a node outcome to a glyph + colour, matching the project's
# explainability-first presentation.
_OUTCOME_STYLE = {
    "ALLOW": (_PASS, "green"),
    "PASS": (_PASS, "green"),
    "NO_CONFIG": (_FAIL, "red"),
    "LIMIT_EXCEEDED": (_FAIL, "red"),
    "BLOCK": (_FAIL, "red"),
    "ANOMALY": (_WARN, "yellow"),
    "SPIKE_DETECTED": (_WARN, "yellow"),
    "FLAG": (_WARN, "yellow"),
    "SKIPPED_LOW_BASELINE": (_SKIP, "dim"),
}


def trace_command(
    decision_id: str = typer.Argument(..., help="Decision ID returned by `devrate check`"),
    base_url: str = typer.Option(
        "http://localhost:8000",
        "--base-url",
        help="Devrate API base URL",
    ),
):
    api = DevrateAPI(base_url)

    try:
        result = api.get_trace(decision_id)
    except Exception as e:
        console.print(f"[red]API Error:[/red] {e}")
        raise typer.Exit(1)

    console.print(f"[bold]Trace for[/bold] {result['decision_id']}\n")

    for step in result.get("steps", []):
        outcome = step.get("outcome", "")
        default_glyph = "•" if _UNICODE else "*"
        glyph, color = _OUTCOME_STYLE.get(outcome, (default_glyph, "white"))

        node = step.get("node", "")
        meta = step.get("metadata", {})
        meta_str = "  ".join(f"{k}={v}" for k, v in meta.items()) if meta else ""

        console.print(
            f"[{color}]{glyph}[/{color}] "
            f"[bold]{node:<22}[/bold] "
            f"[{color}]{outcome:<22}[/{color}] "
            f"[dim]{meta_str}[/dim]"
        )
