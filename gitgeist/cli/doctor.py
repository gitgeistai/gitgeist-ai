# gitgeist/cli/doctor.py
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from gitgeist.utils.recovery import RecoveryManager
from gitgeist.utils.error_handler import ErrorHandler
from gitgeist.core.validator import SystemValidator, GitValidator, ConfigValidator

console = Console()


def doctor_command():
    """Diagnose and fix common Gitgeist issues"""
    console.print("🩺 [bold blue]Gitgeist Doctor[/bold blue] - System Diagnosis\n")
    
    recovery = RecoveryManager()
    diagnosis = recovery.diagnose_system()
    
    # Create diagnosis table
    table = Table(title="System Health Check")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Action", style="yellow")
    
    # Configuration
    if diagnosis["config_exists"] and diagnosis["config_valid"]:
        table.add_row("Configuration", "✅ Healthy", "None")
    elif diagnosis["config_exists"]:
        table.add_row("Configuration", "⚠️ Corrupted", "Repair available")
    else:
        table.add_row("Configuration", "❌ Missing", "Run 'gitgeist init'")
    
    # Git repository
    if diagnosis["git_repo"]:
        table.add_row("Git Repository", "✅ Valid", "None")
    else:
        table.add_row("Git Repository", "❌ Invalid", "Run 'git init'")
    
    # Data directory
    if diagnosis["data_dir"]:
        table.add_row("Data Directory", "✅ Present", "None")
    else:
        table.add_row("Data Directory", "⚠️ Missing", "Will be created")
    
    # Dependencies
    if diagnosis["dependencies"]:
        table.add_row("Dependencies", "✅ Complete", "None")
    else:
        table.add_row("Dependencies", "❌ Missing", "Install required packages")
    
    console.print(table)
    
    # Offer repairs
    issues_found = not all(diagnosis.values())
    
    if issues_found:
        console.print("\n🔧 [bold]Issues detected![/bold]")
        
        if typer.confirm("Would you like to attempt automatic repairs?"):
            perform_repairs(recovery, diagnosis)
    else:
        console.print("\n✅ [bold green]All systems healthy![/bold green]")


def perform_repairs(recovery: RecoveryManager, diagnosis: dict):
    """Perform automatic repairs"""
    console.print("\n🔧 Starting repairs...\n")
    
    # Repair configuration
    if not diagnosis["config_valid"]:
        console.print("Repairing configuration...")
        if recovery.repair_config():
            console.print("✅ Configuration repaired")
        else:
            console.print("❌ Configuration repair failed")
            if typer.confirm("Reset to defaults?"):
                recovery.reset_to_defaults()
                console.print("✅ Configuration reset to defaults")
    
    # Clean data directory
    if diagnosis["data_dir"]:
        console.print("Cleaning data directory...")
        if recovery.clean_data_directory():
            console.print("✅ Data directory cleaned")
    
    # Check dependencies
    if not diagnosis["dependencies"]:
        missing = SystemValidator.validate_dependencies()
        console.print(f"❌ Missing dependencies: {', '.join(missing)}")
        console.print("💡 Install with: pip install gitgeist[dev]")
    
    console.print("\n🎉 Repair process completed!")
    console.print("Run 'gitgeist doctor' again to verify fixes.")


if __name__ == "__main__":
    doctor_command()