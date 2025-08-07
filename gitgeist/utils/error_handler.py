# gitgeist/utils/error_handler.py
import functools
import traceback
from typing import Any, Callable, Optional, Type, Union

from rich.console import Console
from rich.panel import Panel

from gitgeist.utils.exceptions import GitgeistError
from gitgeist.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


class ErrorHandler:
    """Centralized error handling with user-friendly messages"""

    @staticmethod
    def handle_error(error: Exception, context: str = "", show_traceback: bool = False) -> None:
        """Handle errors with appropriate user feedback"""
        
        if isinstance(error, GitgeistError):
            # Custom Gitgeist errors - show user-friendly message
            console.print(f"❌ {error}", style="red")
            if error.suggestion:
                console.print(f"💡 {error.suggestion}", style="yellow")
        elif isinstance(error, FileNotFoundError):
            console.print("❌ Configuration not found. Run 'gitgeist init' first.", style="red")
        elif isinstance(error, PermissionError):
            console.print("❌ Permission denied. Check file permissions.", style="red")
        elif "git" in str(error).lower():
            console.print(f"❌ Git error: {error}", style="red")
            console.print("💡 Make sure you're in a git repository", style="yellow")
        elif "ollama" in str(error).lower() or "connection" in str(error).lower():
            console.print("❌ Cannot connect to Ollama", style="red")
            console.print("💡 Start Ollama with: ollama serve", style="yellow")
        else:
            # Generic error
            console.print(f"❌ {context}: {error}" if context else f"❌ {error}", style="red")
        
        if show_traceback:
            console.print("\n[dim]Full traceback:[/dim]")
            console.print(traceback.format_exc(), style="dim")
        
        logger.error(f"{context}: {error}", exc_info=True)

    @staticmethod
    def safe_execute(func: Callable, *args, context: str = "", **kwargs) -> Optional[Any]:
        """Execute function with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle_error(e, context)
            return None


def handle_errors(context: str = "", show_traceback: bool = False):
    """Decorator for automatic error handling"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.handle_error(e, context or func.__name__, show_traceback)
                raise
        return wrapper
    return decorator


def safe_async_execute(context: str = ""):
    """Decorator for async functions with error handling"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.handle_error(e, context or func.__name__)
                return None
        return wrapper
    return decorator