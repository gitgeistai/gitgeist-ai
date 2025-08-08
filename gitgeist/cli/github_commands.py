# gitgeist/cli/github_commands.py
import asyncio
import os
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from gitgeist.integrations.github import GitHubIntegration
from gitgeist.utils.error_handler import handle_errors

console = Console()
github_app = typer.Typer(name="github", help="GitHub integration commands")


@github_app.command("pr")
@handle_errors("Create PR")
def create_pull_request(
    title: Optional[str] = typer.Option(None, "--title", "-t", help="PR title"),
    body: Optional[str] = typer.Option(None, "--body", "-b", help="PR body"),
    token: Optional[str] = typer.Option(None, "--token", help="GitHub token")
):
    """Create pull request from current branch"""
    
    # Get token from environment if not provided
    if not token:
        token = os.getenv("GITHUB_TOKEN")
    
    if not token:
        console.print("❌ GitHub token required. Set GITHUB_TOKEN environment variable or use --token", style="red")
        raise typer.Exit(1)
    
    async def create_pr():
        github = GitHubIntegration(token)
        
        try:
            pr = await github.auto_create_pr_from_branch(title, body)
            
            console.print(Panel(
                f"✅ [bold green]Pull Request Created![/bold green]\n\n"
                f"Title: {pr['title']}\n"
                f"URL: {pr['html_url']}\n"
                f"Number: #{pr['number']}",
                title="🚀 GitHub PR",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(f"❌ Failed to create PR: {e}", style="red")
            raise typer.Exit(1)
    
    asyncio.run(create_pr())


@github_app.command("issues")
@handle_errors("List issues")
def list_issues(
    state: str = typer.Option("open", "--state", "-s", help="Issue state (open/closed)"),
    token: Optional[str] = typer.Option(None, "--token", help="GitHub token")
):
    """List repository issues"""
    
    # Get token from environment if not provided
    if not token:
        token = os.getenv("GITHUB_TOKEN")
    
    async def get_issues():
        github = GitHubIntegration(token)
        repo_info = github.get_repo_from_remote()
        
        if not repo_info:
            console.print("❌ Not a GitHub repository", style="red")
            raise typer.Exit(1)
        
        owner, repo = repo_info
        
        try:
            issues = await github.get_issues(owner, repo, state)
            
            if not issues:
                console.print(f"No {state} issues found", style="yellow")
                return
            
            console.print(f"\n📋 [bold]{state.title()} Issues for {owner}/{repo}[/bold]\n")
            
            for issue in issues[:10]:  # Show first 10
                title = issue['title']
                number = issue['number']
                labels = [label['name'] for label in issue.get('labels', [])]
                label_text = f" [{', '.join(labels)}]" if labels else ""
                
                console.print(f"#{number}: {title}{label_text}")
            
            if len(issues) > 10:
                console.print(f"\n... and {len(issues) - 10} more issues")
                
        except Exception as e:
            console.print(f"❌ Failed to get issues: {e}", style="red")
            raise typer.Exit(1)
    
    asyncio.run(get_issues())


@github_app.command("repo")
@handle_errors("Repository info")
def repository_info():
    """Show GitHub repository information"""
    github = GitHubIntegration()
    repo_info = github.get_repo_from_remote()
    
    if not repo_info:
        console.print("❌ Not a GitHub repository", style="red")
        raise typer.Exit(1)
    
    owner, repo = repo_info
    console.print(f"📁 Repository: [bold]{owner}/{repo}[/bold]")
    console.print(f"🔗 URL: https://github.com/{owner}/{repo}")


if __name__ == "__main__":
    github_app()