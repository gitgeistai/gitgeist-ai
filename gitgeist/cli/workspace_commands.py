# gitgeist/cli/workspace_commands.py
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from gitgeist.core.workspace import WorkspaceManager, MultiRepoCommitGenerator
from gitgeist.utils.error_handler import handle_errors

console = Console()
workspace_app = typer.Typer(name="workspace", help="Multi-repository workspace management")


@workspace_app.command("add")
@handle_errors("Add repository")
def add_repository(
    path: str = typer.Argument(..., help="Path to git repository"),
    alias: Optional[str] = typer.Option(None, "--alias", "-a", help="Repository alias")
):
    """Add repository to workspace"""
    workspace = WorkspaceManager()
    
    try:
        workspace.add_repository(path, alias)
        repo_alias = alias or Path(path).name
        console.print(f"✅ Added repository: [bold]{repo_alias}[/bold] -> {path}", style="green")
    except Exception as e:
        console.print(f"❌ Failed to add repository: {e}", style="red")
        raise typer.Exit(1)


@workspace_app.command("remove")
@handle_errors("Remove repository")
def remove_repository(
    alias: str = typer.Argument(..., help="Repository alias to remove")
):
    """Remove repository from workspace"""
    workspace = WorkspaceManager()
    
    if workspace.remove_repository(alias):
        console.print(f"✅ Removed repository: [bold]{alias}[/bold]", style="green")
    else:
        console.print(f"❌ Repository not found: {alias}", style="red")
        raise typer.Exit(1)


@workspace_app.command("list")
@handle_errors("List repositories")
def list_repositories():
    """List all repositories in workspace"""
    workspace = WorkspaceManager()
    repositories = workspace.list_repositories()
    
    if not repositories:
        console.print("No repositories in workspace", style="yellow")
        return
    
    table = Table(title="Workspace Repositories")
    table.add_column("Alias", style="cyan")
    table.add_column("Path", style="blue")
    table.add_column("Status", style="green")
    
    for alias, info in repositories.items():
        status = "🟢 Active" if info.get("active", False) else "⚪ Inactive"
        table.add_row(alias, info["path"], status)
    
    console.print(table)


@workspace_app.command("activate")
@handle_errors("Activate repository")
def activate_repository(
    alias: str = typer.Argument(..., help="Repository alias to activate")
):
    """Set active repository"""
    workspace = WorkspaceManager()
    
    if workspace.set_active_repository(alias):
        console.print(f"✅ Activated repository: [bold]{alias}[/bold]", style="green")
    else:
        console.print(f"❌ Repository not found: {alias}", style="red")
        raise typer.Exit(1)


@workspace_app.command("status")
@handle_errors("Workspace status")
def workspace_status():
    """Show status of all repositories"""
    workspace = WorkspaceManager()
    multi_repo = MultiRepoCommitGenerator(workspace)
    
    status = multi_repo.get_status_all_repositories()
    
    if not status:
        console.print("No repositories in workspace", style="yellow")
        return
    
    table = Table(title="Repository Status")
    table.add_column("Repository", style="cyan")
    table.add_column("Changes", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Active", style="blue")
    
    for alias, info in status.items():
        if "error" in info:
            changes = "Error"
            status_text = info["error"][:50]
        else:
            changes = str(info["changes"])
            status_text = "Clean" if info["clean"] else "Modified"
        
        active = "Yes" if info["active"] else "No"
        table.add_row(alias, changes, status_text, active)
    
    console.print(table)


@workspace_app.command("commit-all")
@handle_errors("Commit all repositories")
def commit_all_repositories(
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Commit message"),
    auto: bool = typer.Option(False, "--auto", help="Auto-commit without confirmation")
):
    """Commit changes in all active repositories"""
    workspace = WorkspaceManager()
    multi_repo = MultiRepoCommitGenerator(workspace)
    
    repositories = workspace.list_repositories()
    active_repos = [alias for alias, info in repositories.items() if info.get("active", True)]
    
    if not active_repos:
        console.print("No active repositories", style="yellow")
        return
    
    console.print(f"Will commit to {len(active_repos)} repositories: {', '.join(active_repos)}")
    
    if not auto and not typer.confirm("Continue?"):
        console.print("Cancelled", style="yellow")
        return
    
    console.print("Committing to all repositories...")
    results = multi_repo.commit_all_repositories(message)
    
    # Show results
    table = Table(title="Commit Results")
    table.add_column("Repository", style="cyan")
    table.add_column("Result", style="green")
    
    for alias, success in results.items():
        result = "✅ Success" if success else "❌ Failed"
        table.add_row(alias, result)
    
    console.print(table)
    
    success_count = sum(1 for success in results.values() if success)
    console.print(f"\n{success_count}/{len(results)} repositories committed successfully")


if __name__ == "__main__":
    workspace_app()