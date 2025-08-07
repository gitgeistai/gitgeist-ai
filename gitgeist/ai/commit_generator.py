# gitgeist/ai/commit_generator.py - Enhanced commit generation with semantic understanding

import asyncio
import subprocess
import json
from typing import Dict, List, Optional
from datetime import datetime

from gitgeist.core.config import GitgeistConfig
from gitgeist.ai.llm_client import OllamaClient
from gitgeist.ai.prompts import COMMIT_PROMPTS
from gitgeist.utils.logger import get_logger

logger = get_logger(__name__)

class CommitGenerator:
    """Generates intelligent commit messages using semantic analysis"""
    
    def __init__(self, config: GitgeistConfig):
        self.config = config
        self.llm_client = OllamaClient(config)
        
    def _analyze_git_status(self) -> Dict:
        """Get current git status and changes"""
        try:
            # Get staged/unstaged files
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            
            files = {'staged': [], 'modified': [], 'added': [], 'deleted': []}
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                index_status = line[0]
                work_status = line[1]
                filepath = line[3:]
                
                if index_status != ' ':  # Staged changes
                    files['staged'].append(filepath)
                elif work_status == 'M':
                    files['modified'].append(filepath)
                elif work_status == '?':
                    files['added'].append(filepath)
                elif work_status == 'D':
                    files['deleted'].append(filepath)
            
            return files
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git status failed: {e}")
            return {'error': str(e)}
    
    def _get_diff_stats(self) -> Dict:
        """Get detailed diff statistics"""
        try:
            result = subprocess.run(['git', 'diff', '--stat'], 
                                  capture_output=True, text=True, check=True)
            
            lines = result.stdout.strip().split('\n')
            stats = {'files_changed': 0, 'insertions': 0, 'deletions': 0, 'files': []}
            
            for line in lines:
                if ' file' in line and 'changed' in line:
                    # Parse summary line: "X files changed, Y insertions(+), Z deletions(-)"
                    parts = line.split(',')
                    stats['files_changed'] = int(parts[0].split()[0])
                    
                    for part in parts[1:]:
                        if 'insertion' in part:
                            stats['insertions'] = int(part.strip().split()[0])
                        elif 'deletion' in part:
                            stats['deletions'] = int(part.strip().split()[0])
                elif '|' in line:
                    # Parse file-specific stats: "filename | 5 ++---"
                    parts = line.split('|')
                    if len(parts) == 2:
                        filename = parts[0].strip()
                        changes = parts[1].strip()
                        stats['files'].append({'name': filename, 'changes': changes})
            
            return stats
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git diff failed: {e}")
            return {'error': str(e)}
    
    async def generate_from_analyses(self, change_analyses: List[Dict]) -> str:
        """Generate commit message from semantic change analyses"""
        
        # Aggregate semantic changes
        semantic_summary = {
            'total_files': len(change_analyses),
            'code_files': len([a for a in change_analyses if a.get('language')]),
            'functions_added': [],
            'functions_removed': [],
            'functions_modified': [],
            'classes_added': [],
            'classes_removed': [],
            'new_imports': False,
            'languages': set()
        }
        
        file_details = []
        
        for analysis in change_analyses:
            file_info = {
                'path': analysis['filepath'],
                'type': analysis['event_type'],
                'language': analysis.get('language', 'unknown')
            }
            
            if analysis.get('language'):
                semantic_summary['languages'].add(analysis['language'])
            
            if analysis.get('semantic_changes'):
                changes = analysis['semantic_changes']
                semantic_summary['functions_added'].extend(changes.get('functions_added', []))
                semantic_summary['functions_removed'].extend(changes.get('functions_removed', []))
                semantic_summary['functions_modified'].extend(changes.get('functions_modified', []))
                semantic_summary['classes_added'].extend(changes.get('classes_added', []))
                semantic_summary['classes_removed'].extend(changes.get('classes_removed', []))
                
                if changes.get('imports_changed'):
                    semantic_summary['new_imports'] = True
                
                file_info['semantic_changes'] = changes
            
            file_details.append(file_info)
        
        # Get git status for additional context
        git_status = self._analyze_git_status()
        diff_stats = self._get_diff_stats()
        
        # Generate commit message using LLM
        prompt_context = {
            'semantic_summary': semantic_summary,
            'file_details': file_details[:5],  # Limit for prompt size
            'git_status': git_status,
            'diff_stats': diff_stats,
            'commit_style': self.config.commit_style
        }
        
        return await self._generate_commit_message(prompt_context)
    
    async def _generate_commit_message(self, context: Dict) -> str:
        """Generate commit message using LLM with rich context"""
        
        # Choose prompt template based on commit style
        if self.config.commit_style == "conventional":
            prompt_template = COMMIT_PROMPTS['conventional']
        elif self.config.commit_style == "semantic":
            prompt_template = COMMIT_PROMPTS['semantic']
        else:
            prompt_template = COMMIT_PROMPTS['default']
        
        # Build the prompt
        semantic = context['semantic_summary']
        
        prompt = prompt_template.format(
            total_files=semantic['total_files'],
            code_files=semantic['code_files'],
            languages=', '.join(semantic['languages']) if semantic['languages'] else 'none',
            functions_added=len(semantic['functions_added']),
            functions_removed=len(semantic['functions_removed']),
            functions_modified=len(semantic['functions_modified']),
            classes_added=len(semantic['classes_added']),
            classes_removed=len(semantic['classes_removed']),
            functions_added_list=', '.join(semantic['functions_added'][:3]) if semantic['functions_added'] else 'none',
            classes_added_list=', '.join(semantic['classes_added'][:3]) if semantic['classes_added'] else 'none',
            file_changes=self._format_file_changes(context['file_details']),
            insertions=context['diff_stats'].get('insertions', 0),
            deletions=context['diff_stats'].get('deletions', 0)
        )
        
        try:
            response = await self.llm_client.generate(prompt)
            commit_message = response.strip()
            
            # Post-process commit message
            commit_message = self._clean_commit_message(commit_message)
            
            logger.info(f"Generated commit message: {commit_message}")
            return commit_message
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._fallback_commit_message(context)
    
    def _format_file_changes(self, file_details: List[Dict]) -> str:
        """Format file changes for prompt"""
        formatted = []
        for file_info in file_details:
            line = f"- {file_info['path']} ({file_info['language']})"
            if file_info.get('semantic_changes'):
                changes = file_info['semantic_changes']
                change_parts = []
                if changes.get('functions_added'):
                    change_parts.append(f"+{len(changes['functions_added'])} funcs")
                if changes.get('classes_added'):
                    change_parts.append(f"+{len(changes['classes_added'])} classes")
                if changes.get('functions_removed'):
                    change_parts.append(f"-{len(changes['functions_removed'])} funcs")
                
                if change_parts:
                    line += f": {', '.join(change_parts)}"
            
            formatted.append(line)
        
        return '\n'.join(formatted)
    
    def _clean_commit_message(self, message: str) -> str:
        """Clean and validate commit message"""
        # Remove any markdown formatting
        message = message.replace('**', '').replace('*', '')
        
        # Remove quotes if LLM added them
        if message.startswith('"') and message.endswith('"'):
            message = message[1:-1]
        
        # Ensure first line is not too long (72 chars is git standard)
        lines = message.split('\n')
        if lines and len(lines[0]) > 72:
            # Try to shorten
            first_line = lines[0][:69] + "..."
            if len(lines) > 1:
                message = first_line + '\n\n' + '\n'.join(lines[1:])
            else:
                message = first_line
        
        return message
    
    def _fallback_commit_message(self, context: Dict) -> str:
        """Generate simple fallback commit message if LLM fails"""
        semantic = context['semantic_summary']
        
        if semantic['functions_added']:
            return f"feat: add {len(semantic['functions_added'])} new functions"
        elif semantic['functions_removed']:
            return f"refactor: remove {len(semantic['functions_removed'])} functions"
        elif semantic['classes_added']:
            return f"feat: add {len(semantic['classes_added'])} new classes"
        else:
            return f"chore: update {semantic['total_files']} files"
    
    async def create_commit(self, message: str, add_all: bool = True) -> bool:
        """Actually create the git commit"""
        try:
            # Add files if requested
            if add_all:
                subprocess.run(['git', 'add', '.'], check=True)
            
            # Create commit
            result = subprocess.run(['git', 'commit', '-m', message], 
                                  capture_output=True, text=True, check=True)
            
            logger.info(f"✅ Commit created: {message}")
            logger.debug(f"Git output: {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Commit failed: {e}")
            logger.error(f"Git error: {e.stderr}")
            return False
    
    async def generate_commit_message(self, custom_message: Optional[str] = None) -> str:
        """Main method to generate commit message for current changes"""
        if custom_message:
            return custom_message
        
        # Analyze current changes (this would integrate with your AST parser)
        git_status = self._analyze_git_status()
        if 'error' in git_status:
            return "chore: update files"
        
        # For now, create mock analysis - in real implementation, 
        # this would use your AST parser on the changed files
        mock_analyses = []
        for filepath in git_status.get('modified', []) + git_status.get('added', []):
            mock_analyses.append({
                'filepath': filepath,
                'event_type': 'modified',
                'language': 'python' if filepath.endswith('.py') else None,
                'semantic_changes': {
                    'functions_added': ['new_function'] if 'new' in filepath else [],
                    'functions_removed': [],
                    'functions_modified': ['existing_function'] if filepath in git_status.get('modified', []) else [],
                    'classes_added': [],
                    'classes_removed': [],
                    'imports_changed': False
                }
            })
        
        return await self.generate_from_analyses(mock_analyses)
    
    async def generate_and_commit(self, custom_message: Optional[str] = None, auto_commit: bool = False) -> Dict:
        """Generate commit message and optionally create commit"""
        try:
            # Generate commit message
            message = await self.generate_commit_message(custom_message)
            
            result = {'message': message, 'committed': False}
            
            if auto_commit:
                success = await self.create_commit(message)
                result['committed'] = success
            
            return result
            
        except Exception as e:
            logger.error(f"Generate and commit failed: {e}")
            return {'error': str(e)}


# Usage example
if __name__ == "__main__":
    import asyncio
    
    async def test_commit_generator():
        config = GitgeistConfig.load()
        generator = CommitGenerator(config)
        
        # Test commit message generation
        message = await generator.generate_commit_message()
        print(f"Generated: {message}")
        
        # Optionally create the commit
        # success = await generator.create_commit(message)
        # print(f"Commit created: {success}")
    
    asyncio.run(test_commit_generator())