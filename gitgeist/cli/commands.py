# gitgeist/cli/commands.py
import asyncio
import json
import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from gitgeist.ai.commit_generator import CommitGenerator
from gitgeist.ai.llm_client import OllamaClient
from gitgeist.core.config import GitgeistConfig
from gitgeist.core.git_handler import GitHandler
from gitgeist.core.schema import validate_config
from gitgeist.core.watcher import GitgeistWatcher
from gitgeist.utils.exceptions import GitgeistError, ValidationError
from gitgeist.utils.error_handler import ErrorHandler, handle_errors
from gitgeist.utils.logger import set_log_level, setup_logger
from gitgeist.core.validator import ConfigValidator, GitValidator, SystemValidator

app = typer.Typer(
    name="gitgeist",
    help="🧠 Gitgeist - Autonomous AI Git Agent\n\nGenerate intelligent commit messages using local LLMs and semantic code analysis.",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()


def print_logo():
    """Print Gitgeist logo"""
    console.print(
        "🧠 [bold blue]Gitgeist[/bold blue] - Autonomous AI Git Agent", style="bold"
    )


@app.command()
@handle_errors("Initialization")
def init(
    autonomous: bool = typer.Option(
        False, "--autonomous", "-a", help="Enable autonomous mode"
    ),
    model: str = typer.Option("llama3.2", "--model", "-m", help="LLM model to use"),
    host: str = typer.Option(
        "http://localhost:11434", "--host", help="Ollama host URL"
    ),
    style: str = typer.Option(
        "conventional",
        "--style",
        "-s",
        help="Commit message style (conventional/semantic/default)",
    ),
):
    """Initialize Gitgeist in current repository"""
    print_logo()

    # Validate inputs
    ConfigValidator.validate_model_name(model)
    ConfigValidator.validate_host_url(host)
    ConfigValidator.validate_commit_style(style)
    
    # Check system dependencies
    missing_deps = SystemValidator.validate_dependencies()
    if missing_deps:
        console.print(f"❌ Missing dependencies: {', '.join(missing_deps)}", style="red")
        console.print("💡 Install with: pip install gitgeist[dev]", style="yellow")
        raise typer.Exit(1)
    
    # Validate git repository
    GitValidator.validate_repository()
    SystemValidator.validate_disk_space()

    # Create configuration
    config = GitgeistConfig(
        autonomous_mode=autonomous, llm_model=model, llm_host=host, commit_style=style
    )

    # Validate configuration
    config_dict = {
        k: str(v) if isinstance(v, Path) else v for k, v in config.__dict__.items()
    }
    validation_errors = validate_config(config_dict)
    if validation_errors:
        console.print("❌ Configuration validation failed:", style="red")
        for error in validation_errors:
            console.print(f"  • {error}", style="red")
        raise typer.Exit(1)

    # Save configuration
    config.save()

    # Create necessary directories
    config.data_dir.mkdir(parents=True, exist_ok=True)
    config.log_file.parent.mkdir(parents=True, exist_ok=True)

    # Test Ollama connection
    async def test_connection():
        llm_client = OllamaClient(config)
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}")
        ) as progress:
            task = progress.add_task("Testing Ollama connection...", total=None)

            health = await llm_client.health_check()
            if health:
                progress.update(task, description="✅ Ollama connected")

                # Check model availability
                progress.update(task, description=f"Checking model {model}...")
                model_available = await llm_client.check_model_availability()
                if model_available:
                    progress.update(task, description=f"✅ Model {model} available")
                else:
                    progress.update(task, description=f"⚠️  Model {model} not found")
                    console.print(
                        f"Model '{model}' not found. Install with: ollama pull {model}",
                        style="yellow",
                    )
            else:
                progress.update(task, description="❌ Ollama not responding")
                console.print(
                    "Ollama not running. Start with: ollama serve", style="red"
                )

    asyncio.run(test_connection())

    # Success message
    panel_content = f"""✅ Gitgeist initialized successfully!

Configuration:
• Autonomous mode: {'🤖 Enabled' if autonomous else '💡 Suggestion mode'}
• LLM Model: {model}
• Host: {host}
• Commit style: {style}
• Config saved to: .gitgeist.json

Next steps:
• Start watching: [bold]gitgeist watch[/bold]
• Generate commit: [bold]gitgeist commit[/bold]
• View status: [bold]gitgeist status[/bold]"""

    console.print(Panel(panel_content, title="🎉 Setup Complete", border_style="green"))


@app.command()
@handle_errors("Watch mode")
def watch():
    """Start watching repository for changes"""
    print_logo()

    try:
        config = GitgeistConfig.load()
        setup_logger(config.log_file)

        # Validate git repository
        GitValidator.validate_repository()

        watcher = GitgeistWatcher(config)

        mode_text = "🤖 Autonomous" if config.autonomous_mode else "💡 Suggestion"
        console.print(f"👀 Watching repository in {mode_text} mode...")
        console.print("Press Ctrl+C to stop", style="dim")

        watcher.start()

    except KeyboardInterrupt:
        console.print("\n👋 Stopped watching", style="yellow")
    except Exception as e:
        ErrorHandler.handle_error(e, "Watch mode")
        raise typer.Exit(1)


@app.command()
def commit(
    message: Optional[str] = typer.Option(
        None, "--message", "-m", help="Custom commit message"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be committed"
    ),
    auto: bool = typer.Option(
        False, "--auto", help="Automatically commit without confirmation"
    ),
):
    """Generate and create an AI commit"""
    print_logo()

    async def run_commit():
        try:
            config = GitgeistConfig.load()
            setup_logger(config.log_file)

            generator = CommitGenerator(config)

            # Check for changes
            git_handler = GitHandler()
            if not git_handler.has_uncommitted_changes():
                console.print("ℹ️  No uncommitted changes found", style="blue")
                return

            if dry_run:
                # Show analysis without committing
                console.print("🔍 [bold]Dry run mode[/bold] - analyzing changes...\n")

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                ) as progress:
                    task = progress.add_task(
                        "Analyzing repository changes...", total=None
                    )

                    # Get enhanced diff summary
                    diff_summary = git_handler.get_enhanced_diff_summary()
                    progress.update(task, description="✅ Analysis complete")

                # Display results
                summary = diff_summary["summary"]

                table = Table(title="📊 Change Analysis")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")

                table.add_row("Files changed", str(summary["total_files"]))
                table.add_row("Code files", str(summary["code_files"]))
                table.add_row("Languages", ", ".join(summary["languages"]) or "none")
                table.add_row("Functions added", str(summary["functions_added"]))
                table.add_row("Functions removed", str(summary["functions_removed"]))
                table.add_row("Classes added", str(summary["classes_added"]))

                console.print(table)

                # Initialize memory if needed for better suggestions
                stats = generator.memory.get_memory_stats()
                if stats['commits_stored'] == 0:
                    progress.update(task, description="Loading git history for better suggestions...")
                    generator.populate_memory_from_history(50)
                
                # Generate message preview
                progress.update(task, description="Generating commit message...")
                console.print("\n💡 [bold]Generated commit message:[/bold]")
                commit_msg = await generator.generate_commit_message(message)
                console.print(Panel(commit_msg, border_style="blue"))
                
                # Show RAG context if available
                try:
                    similar_commits = generator.memory.find_similar_commits(
                        f"files: {', '.join([f['name'] for f in diff_summary['summary'].get('files', [])][:3])}", 
                        limit=2
                    )
                    if similar_commits:
                        console.print("\n🔍 [bold]Similar past commits:[/bold]")
                        for commit in similar_commits:
                            similarity = commit.get('similarity', 0)
                            if similarity > 0.3:
                                console.print(f"  • {commit['message']} (similarity: {similarity:.2f})")
                except Exception:
                    pass
                
                # Show branch info
                branch_type = generator.branch_manager.get_branch_type()
                current_branch = generator.branch_manager.get_current_branch()
                console.print(f"\n🌳 [bold]Branch:[/bold] {current_branch} ({branch_type})")
                
                # Show performance stats
                try:
                    perf_stats = generator.analyzer.get_performance_stats()
                    cache_hits = perf_stats['cache']['entries']
                    if cache_hits > 0:
                        console.print(f"⚡ Cache: {cache_hits} entries")
                except Exception:
                    pass

            else:
                # Generate and optionally commit
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                ) as progress:
                    task = progress.add_task(
                        "Initializing memory...", total=None
                    )
                    
                    # Initialize memory if needed
                    stats = generator.memory.get_memory_stats()
                    if stats['commits_stored'] == 0:
                        progress.update(task, description="Loading git history into memory...")
                        generator.populate_memory_from_history(50)
                    
                    progress.update(task, description="Generating intelligent commit message...")
                    result = await generator.generate_and_commit(
                        custom_message=message, auto_commit=auto
                    )

                    progress.update(task, description="✅ Generation complete")

                if result.get("committed"):
                    console.print(
                        f"✅ [bold green]Committed:[/bold green] {result['message']}"
                    )
                elif result.get("message"):
                    console.print(
                        f"💡 [bold blue]Generated message:[/bold blue] {result['message']}"
                    )

                    if not auto:
                        if typer.confirm("Create this commit?"):
                            success = await generator.create_commit(result["message"])
                            if success:
                                console.print("✅ Commit created!", style="green")
                            else:
                                console.print("❌ Failed to create commit", style="red")
                        else:
                            console.print("Commit cancelled", style="yellow")
                else:
                    console.print("❌ Failed to generate commit message", style="red")

        except FileNotFoundError:
            console.print(
                "❌ No configuration found. Run 'gitgeist init' first.", style="red"
            )
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"❌ Error: {e}", style="red")
            raise typer.Exit(1)

    asyncio.run(run_commit())


@app.command()
def status():
    """Show Gitgeist and repository status"""
    print_logo()

    async def show_status():
        try:
            config = GitgeistConfig.load()

            # Git status
            git_handler = GitHandler()
            if not git_handler.is_git_repo():
                console.print("❌ Not a git repository", style="red")
                return

            git_status = git_handler.get_git_status()
            recent_commits = git_handler.get_recent_commits(3)

            # Create status table
            table = Table(title="📊 Repository Status")
            table.add_column("Category", style="cyan")
            table.add_column("Status", style="green")

            table.add_row("Configuration", "✅ Loaded from .gitgeist.json")
            table.add_row("Git Repository", "✅ Valid")
            table.add_row(
                "Autonomous Mode",
                "🤖 Enabled" if config.autonomous_mode else "💡 Suggestion mode",
            )
            table.add_row("LLM Model", config.llm_model)
            table.add_row("Commit Style", config.commit_style)

            # File changes
            total_changes = len(git_status.get("modified", [])) + len(
                git_status.get("added", [])
            )
            table.add_row("Uncommitted Changes", str(total_changes))

            console.print(table)

            # Recent commits
            if recent_commits:
                console.print("\n📜 [bold]Recent Commits:[/bold]")
                for commit in recent_commits:
                    console.print(f"  • {commit['date']} - {commit['message'][:60]}...")
            
            # Memory stats
            try:
                from gitgeist.memory.vector_store import GitgeistMemory
                memory = GitgeistMemory(config.data_dir)
                stats = memory.get_memory_stats()
                
                console.print("\n🧠 [bold]Memory Stats:[/bold]")
                console.print(f"  • Commits stored: {stats['commits_stored']}")
                console.print(f"  • Files tracked: {stats['files_tracked']}")
                console.print(f"  • Database size: {stats['db_size_mb']:.1f} MB")
                
                # Initialize memory if empty
                if stats['commits_stored'] == 0:
                    console.print("  ℹ️  Initializing memory with git history...")
                    generator = CommitGenerator(config)
                    generator.populate_memory_from_history(50)
                    console.print("  ✅ Memory initialized")
                    
            except Exception as e:
                console.print(f"\n🧠 [bold]Memory:[/bold] Not available ({e})")
            
            # Branch info
            try:
                from gitgeist.core.branch_manager import BranchManager
                branch_mgr = BranchManager()
                current_branch = branch_mgr.get_current_branch()
                branch_type = branch_mgr.get_branch_type()
                is_protected = branch_mgr.is_protected_branch()
                
                console.print("\n🌳 [bold]Branch Info:[/bold]")
                console.print(f"  • Current: {current_branch} ({branch_type})")
                console.print(f"  • Protected: {'Yes' if is_protected else 'No'}")
                console.print(f"  • Auto-commit: {'No' if is_protected else 'Yes'}")
                
            except Exception as e:
                console.print(f"\n🌳 [bold]Branch:[/bold] Not available ({e})")
            
            # Performance stats
            try:
                from gitgeist.core.performance import OptimizedAnalyzer
                analyzer = OptimizedAnalyzer()
                perf_stats = analyzer.get_performance_stats()
                
                console.print("\n⚡ [bold]Performance:[/bold]")
                console.print(f"  • Cache entries: {perf_stats['cache']['entries']}")
                console.print(f"  • Cache size: {perf_stats['cache']['total_size_mb']:.1f} MB")
                
            except Exception as e:
                console.print(f"\n⚡ [bold]Performance:[/bold] Not available ({e})")

            # Ollama status
            console.print("\n🔌 [bold]Ollama Status:[/bold]")
            llm_client = OllamaClient(config)

            health = await llm_client.health_check()
            if health:
                console.print("  ✅ Ollama is running")

                model_available = await llm_client.check_model_availability()
                if model_available:
                    console.print(f"  ✅ Model {config.llm_model} is available")
                else:
                    console.print(
                        f"  ⚠️  Model {config.llm_model} not found", style="yellow"
                    )
            else:
                console.print("  ❌ Ollama not responding", style="red")
                console.print("     Start with: ollama serve", style="dim")

        except FileNotFoundError:
            console.print(
                "❌ No configuration found. Run 'gitgeist init' first.", style="red"
            )
        except Exception as e:
            console.print(f"❌ Error: {e}", style="red")

    asyncio.run(show_status())


@app.command()
def analyze():
    """Analyze current repository changes"""
    print_logo()

    try:
        config = GitgeistConfig.load()
        git_handler = GitHandler()

        if not git_handler.is_git_repo():
            console.print("❌ Not a git repository", style="red")
            raise typer.Exit(1)

        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}")
        ) as progress:
            task = progress.add_task("Analyzing repository...", total=None)

            diff_summary = git_handler.get_enhanced_diff_summary()
            progress.update(task, description="✅ Analysis complete")

        if "error" in diff_summary:
            console.print(f"❌ Analysis failed: {diff_summary['error']}", style="red")
            return

        summary = diff_summary["summary"]
        semantic_changes = diff_summary.get("semantic_changes", {})

        # Summary table
        table = Table(title="📊 Repository Analysis")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total files changed", str(summary["total_files"]))
        table.add_row("Code files", str(summary["code_files"]))
        table.add_row("Languages detected", ", ".join(summary["languages"]) or "none")
        table.add_row("Functions added", str(summary["functions_added"]))
        table.add_row("Functions removed", str(summary["functions_removed"]))
        table.add_row("Functions modified", str(summary["functions_modified"]))
        table.add_row("Classes added", str(summary["classes_added"]))
        table.add_row("Classes removed", str(summary["classes_removed"]))

        console.print(table)

        # File details
        if semantic_changes:
            console.print("\n📁 [bold]File Details:[/bold]")

            files_table = Table()
            files_table.add_column("File", style="cyan")
            files_table.add_column("Language", style="magenta")
            files_table.add_column("Changes", style="green")

            for filepath, changes in semantic_changes.items():
                change_parts = []
                if changes.get("functions_added"):
                    change_parts.append(f"+{len(changes['functions_added'])} funcs")
                if changes.get("functions_removed"):
                    change_parts.append(f"-{len(changes['functions_removed'])} funcs")
                if changes.get("classes_added"):
                    change_parts.append(f"+{len(changes['classes_added'])} classes")
                if changes.get("classes_removed"):
                    change_parts.append(f"-{len(changes['classes_removed'])} classes")

                change_summary = ", ".join(change_parts) if change_parts else "modified"

                files_table.add_row(
                    Path(filepath).name,
                    changes.get("language", "unknown"),
                    change_summary,
                )

            console.print(files_table)

    except FileNotFoundError:
        console.print(
            "❌ No configuration found. Run 'gitgeist init' first.", style="red"
        )
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    edit: bool = typer.Option(False, "--edit", help="Edit configuration file"),
    reset: bool = typer.Option(False, "--reset", help="Reset to default configuration"),
):
    """Manage Gitgeist configuration"""
    print_logo()

    config_path = Path(".gitgeist.json")

    if reset:
        if config_path.exists() and typer.confirm("Reset configuration to defaults?"):
            config_path.unlink()
            console.print(
                "✅ Configuration reset. Run 'gitgeist init' to recreate.",
                style="green",
            )
        return

    if edit:
        import subprocess
        import sys

        if not config_path.exists():
            console.print(
                "❌ No configuration found. Run 'gitgeist init' first.", style="red"
            )
            return

        editor = os.environ.get(
            "EDITOR", "nano" if sys.platform != "win32" else "notepad"
        )
        subprocess.run([editor, str(config_path)])
        console.print("✅ Configuration file opened for editing", style="green")
        return

    if show or True:  # Default action
        try:
            config = GitgeistConfig.load()

            console.print("⚙️  [bold]Current Configuration:[/bold]\n")

            config_data = {
                "auto_commit": config.auto_commit,
                "commit_style": config.commit_style,
                "llm_model": config.llm_model,
                "llm_host": config.llm_host,
                "temperature": config.temperature,
                "autonomous_mode": config.autonomous_mode,
                "require_confirmation": config.require_confirmation,
                "watch_paths": config.watch_paths,
                "supported_languages": config.supported_languages,
            }

            console.print_json(json.dumps(config_data, indent=2))
            console.print(f"\n📁 Config file: {config_path.absolute()}")

        except FileNotFoundError:
            console.print(
                "❌ No configuration found. Run 'gitgeist init' first.", style="red"
            )


@app.command()
def doctor():
    """Diagnose and fix common Gitgeist issues"""
    from gitgeist.cli.doctor import doctor_command
    doctor_command()


# Add version command
@app.command()
def version():
    """Show Gitgeist version and system info"""
    console.print("🧠 [bold blue]Gitgeist[/bold blue] v0.2.0")
    console.print("Autonomous AI Git Agent")
    console.print("\n[dim]Features:[/dim]")
    console.print("  • Local LLM integration (Ollama)")
    console.print("  • Semantic code analysis (29+ languages)")
    console.print("  • RAG memory system with vector embeddings")
    console.print("  • Branch-aware commit strategies")
    console.print("  • Performance optimization & caching")
    console.print("  • Customizable commit templates")
    console.print("  • Error handling & recovery")
    console.print("\n[dim]Repository:[/dim] https://github.com/gitgeistai/gitgeist-ai")
    console.print("[dim]License:[/dim] MIT")


if __name__ == "__main__":
    app()
