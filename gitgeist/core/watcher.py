# gitgeist/core/watcher.py - Enhanced file watcher with semantic analysis

import asyncio
import time
from pathlib import Path
from typing import Dict, List, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent

from gitgeist.core.config import GitgeistConfig
from gitgeist.analysis.ast_parser import GitgeistASTParser
from gitgeist.ai.commit_generator import CommitGenerator
from gitgeist.utils.logger import get_logger

logger = get_logger(__name__)

class GitgeistFileHandler(FileSystemEventHandler):
    """Enhanced file system event handler with semantic analysis"""
    
    def __init__(self, config: GitgeistConfig, loop=None):
        super().__init__()
        self.config = config
        self.ast_parser = GitgeistASTParser()
        self.commit_generator = CommitGenerator(config)
        self._loop = loop
        
        # Debouncing
        self.pending_changes: Set[str] = set()
        self.last_change_time = time.time()
        self.debounce_delay = 5.0  # seconds
        
        # Change tracking
        self.file_snapshots: Dict[str, Dict] = {}
        
    def should_ignore(self, filepath: str) -> bool:
        """Check if file should be ignored based on patterns"""
        path = Path(filepath)
        
        for pattern in self.config.ignore_patterns:
            if path.match(pattern.replace('*', '**')):
                return True
                
        return False
    
    def analyze_file_change(self, filepath: str, event_type: str) -> Dict:
        """Analyze what changed in a file using AST"""
        if self.should_ignore(filepath):
            return {'ignored': True}
        
        analysis = {
            'filepath': filepath,
            'event_type': event_type,
            'timestamp': time.time(),
            'language': None,
            'semantic_changes': None,
            'text_changes': None
        }
        
        try:
            # Detect if it's a code file
            language = self.ast_parser.detect_language(filepath)
            if language:
                analysis['language'] = language
                
                # Get current file structure
                current_structure = self.ast_parser.analyze_file_structure(filepath)
                
                # Compare with previous snapshot if available
                if filepath in self.file_snapshots:
                    old_structure = self.file_snapshots[filepath]
                    
                    # Semantic diff
                    if current_structure and old_structure:
                        semantic_diff = self._compare_structures(old_structure, current_structure)
                        analysis['semantic_changes'] = semantic_diff
                
                # Update snapshot
                if current_structure:
                    self.file_snapshots[filepath] = current_structure
                    
        except Exception as e:
            logger.error(f"Error analyzing {filepath}: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _compare_structures(self, old: Dict, new: Dict) -> Dict:
        """Compare two file structures for semantic changes"""
        changes = {
            'functions_added': [],
            'functions_removed': [],
            'functions_modified': [],
            'classes_added': [],
            'classes_removed': [],
            'imports_changed': False
        }
        
        # Compare functions
        old_funcs = {f['name']: f for f in old.get('functions', [])}
        new_funcs = {f['name']: f for f in new.get('functions', [])}
        
        changes['functions_added'] = list(set(new_funcs.keys()) - set(old_funcs.keys()))
        changes['functions_removed'] = list(set(old_funcs.keys()) - set(new_funcs.keys()))
        
        # Check for modified functions (line number changes as proxy)
        for name in set(old_funcs.keys()) & set(new_funcs.keys()):
            if old_funcs[name]['start_line'] != new_funcs[name]['start_line']:
                changes['functions_modified'].append(name)
        
        # Compare classes
        old_classes = {c['name']: c for c in old.get('classes', [])}
        new_classes = {c['name']: c for c in new.get('classes', [])}
        
        changes['classes_added'] = list(set(new_classes.keys()) - set(old_classes.keys()))
        changes['classes_removed'] = list(set(old_classes.keys()) - set(new_classes.keys()))
        
        # Compare imports (simple check)
        old_imports = set(i['statement'] for i in old.get('imports', []))
        new_imports = set(i['statement'] for i in new.get('imports', []))
        changes['imports_changed'] = old_imports != new_imports
        
        return changes
    
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path, 'modified')
    
    def on_created(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path, 'created')
    
    def on_deleted(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path, 'deleted')
            # Remove from snapshots
            if event.src_path in self.file_snapshots:
                del self.file_snapshots[event.src_path]
    
    def _handle_file_change(self, filepath: str, event_type: str):
        """Handle individual file changes with debouncing"""
        self.pending_changes.add(filepath)
        self.last_change_time = time.time()
        
        logger.info(f"File {event_type}: {filepath}")
        
        # Immediate analysis for logging
        analysis = self.analyze_file_change(filepath, event_type)
        if not analysis.get('ignored') and analysis.get('semantic_changes'):
            logger.info(f"Semantic changes detected: {analysis['semantic_changes']}")
        
        # Only schedule async operations if we have an event loop
        if hasattr(self, '_loop') and self._loop and self.config.autonomous_mode:
            try:
                asyncio.run_coroutine_threadsafe(self._check_for_commit(), self._loop)
            except Exception as e:
                logger.error(f"Failed to schedule commit check: {e}")
        else:
            # In sync mode, just log the changes
            logger.info(f"Changes detected in {filepath} - use 'gitgeist commit' to create commit")
    
    async def _check_for_commit(self):
        """Check if we should create a commit after debounce delay"""
        await asyncio.sleep(self.debounce_delay)
        
        # Check if enough time has passed since last change
        if time.time() - self.last_change_time >= self.debounce_delay:
            if self.pending_changes and self.config.auto_commit:
                await self._create_commit()
            
            self.pending_changes.clear()
    
    async def _create_commit(self):
        """Create an intelligent commit based on accumulated changes"""
        try:
            logger.info("Creating AI-generated commit...")
            
            # Analyze all pending changes
            change_analyses = []
            for filepath in self.pending_changes:
                analysis = self.analyze_file_change(filepath, 'batch_commit')
                if not analysis.get('ignored'):
                    change_analyses.append(analysis)
            
            if not change_analyses:
                logger.info("No significant changes to commit")
                return
            
            # Generate commit message
            commit_message = await self.commit_generator.generate_from_analyses(change_analyses)
            
            if self.config.autonomous_mode:
                # Auto-commit
                success = await self.commit_generator.create_commit(commit_message)
                if success:
                    logger.info(f"✅ Auto-committed: {commit_message}")
                else:
                    logger.error("❌ Failed to create commit")
            else:
                # Ask for confirmation
                logger.info(f"💡 Suggested commit: {commit_message}")
                # In a real implementation, you'd prompt user here
                
        except Exception as e:
            logger.error(f"Error creating commit: {e}")


class GitgeistWatcher:
    """Main watcher class that orchestrates file monitoring"""
    
    def __init__(self, config: GitgeistConfig):
        self.config = config
        self.observer = Observer()
        self.handler = GitgeistFileHandler(config)
        self.is_running = False
        
    def start(self):
        """Start watching (synchronous)"""
        # Disable auto-commit in sync mode to avoid async issues
        if self.config.autonomous_mode:
            logger.warning("Autonomous mode disabled in sync watch mode. Use async mode for auto-commits.")
            self.config.auto_commit = False
        
        for path in self.config.watch_paths:
            self.observer.schedule(self.handler, path, recursive=True)
        
        self.observer.start()
        self.is_running = True
        logger.info(f"🧠 Gitgeist watching: {self.config.watch_paths}")
        
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    async def start_async(self):
        """Start watching (asynchronous)"""
        # Set event loop for async operations
        self.handler._loop = asyncio.get_running_loop()
        
        for path in self.config.watch_paths:
            self.observer.schedule(self.handler, path, recursive=True)
        
        self.observer.start()
        self.is_running = True
        logger.info(f"🧠 Gitgeist watching: {self.config.watch_paths}")
        
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.stop()
    
    def stop(self):
        """Stop watching"""
        self.is_running = False
        self.observer.stop()
        self.observer.join()
        logger.info("👋 Gitgeist stopped watching")
    
    def get_status(self) -> Dict:
        """Get current watcher status"""
        return {
            'is_running': self.is_running,
            'watched_paths': self.config.watch_paths,
            'files_tracked': len(self.handler.file_snapshots),
            'pending_changes': len(self.handler.pending_changes)
        }


# Usage example
if __name__ == "__main__":
    config = GitgeistConfig.load()
    watcher = GitgeistWatcher(config)
    
    print("🚀 Starting Gitgeist watcher...")
    watcher.start()