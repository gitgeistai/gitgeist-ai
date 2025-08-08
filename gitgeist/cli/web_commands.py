# gitgeist/cli/web_commands.py
import typer
from rich.console import Console

from gitgeist.utils.error_handler import handle_errors

console = Console()
web_app = typer.Typer(name="web", help="Web dashboard commands")


@web_app.command("start")
@handle_errors("Start web server")
def start_dashboard(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8080, "--port", "-p", help="Port to bind to")
):
    """Start the web dashboard"""
    try:
        from gitgeist.web.server import start_server
        console.print(f"🌐 Starting Gitgeist dashboard at http://{host}:{port}")
        console.print("Press Ctrl+C to stop")
        start_server(host, port)
    except ImportError as e:
        console.print("❌ Web dashboard dependencies not installed", style="red")
        console.print("💡 Install with: pip install fastapi uvicorn", style="yellow")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n👋 Dashboard stopped", style="yellow")
    except Exception as e:
        console.print(f"❌ Failed to start dashboard: {e}", style="red")
        raise typer.Exit(1)


if __name__ == "__main__":
    web_app()