# gitgeist/memory/planner.py
from typing import Dict, List, Optional

from gitgeist.memory.vector_store import GitgeistMemory
from gitgeist.utils.logger import get_logger

logger = get_logger(__name__)


class GitgeistPlanner:
    """AI planner for intelligent commit grouping and suggestions"""

    def __init__(self, memory: GitgeistMemory):
        self.memory = memory

    def analyze_changes_with_context(self, current_changes: List[Dict]) -> Dict:
        """Analyze current changes with historical context"""
        try:
            # Extract key information from current changes
            files_changed = [change['filepath'] for change in current_changes]
            
            # Build context query
            query_parts = []
            for change in current_changes:
                if change.get('semantic_changes'):
                    sc = change['semantic_changes']
                    if sc.get('functions_added'):
                        query_parts.append(f"added functions: {', '.join(sc['functions_added'][:3])}")
                    if sc.get('classes_added'):
                        query_parts.append(f"added classes: {', '.join(sc['classes_added'][:2])}")
            
            query = f"Files: {', '.join(files_changed[:3])} | {' | '.join(query_parts)}"
            
            # Find similar historical commits
            similar_commits = self.memory.find_similar_commits(query, limit=3)
            
            # Analyze patterns
            patterns = self._analyze_patterns(current_changes, similar_commits)
            
            return {
                'current_changes': current_changes,
                'similar_commits': similar_commits,
                'patterns': patterns,
                'suggestions': self._generate_suggestions(patterns)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze changes with context: {e}")
            return {'current_changes': current_changes, 'error': str(e)}

    def _analyze_patterns(self, current_changes: List[Dict], 
                         similar_commits: List[Dict]) -> Dict:
        """Analyze patterns in changes and historical commits"""
        patterns = {
            'common_files': [],
            'common_functions': [],
            'change_type': 'unknown',
            'complexity': 'low'
        }
        
        try:
            # Analyze current changes
            all_functions = []
            all_classes = []
            
            for change in current_changes:
                if change.get('semantic_changes'):
                    sc = change['semantic_changes']
                    all_functions.extend(sc.get('functions_added', []))
                    all_functions.extend(sc.get('functions_modified', []))
                    all_classes.extend(sc.get('classes_added', []))
            
            # Determine change type
            if all_functions and not all_classes:
                patterns['change_type'] = 'feature_addition'
            elif all_classes:
                patterns['change_type'] = 'architecture_change'
            elif any('test' in change['filepath'].lower() for change in current_changes):
                patterns['change_type'] = 'testing'
            elif any('fix' in str(change.get('semantic_changes', {})) for change in current_changes):
                patterns['change_type'] = 'bug_fix'
            
            # Determine complexity
            total_changes = len(all_functions) + len(all_classes)
            if total_changes > 5:
                patterns['complexity'] = 'high'
            elif total_changes > 2:
                patterns['complexity'] = 'medium'
            
            # Find common patterns with historical commits
            if similar_commits:
                historical_files = []
                for commit in similar_commits:
                    historical_files.extend(commit.get('files_changed', []))
                
                current_files = [c['filepath'] for c in current_changes]
                patterns['common_files'] = list(set(current_files) & set(historical_files))
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze patterns: {e}")
            return patterns

    def _generate_suggestions(self, patterns: Dict) -> List[str]:
        """Generate intelligent suggestions based on patterns"""
        suggestions = []
        
        try:
            change_type = patterns.get('change_type', 'unknown')
            complexity = patterns.get('complexity', 'low')
            
            # Type-specific suggestions
            if change_type == 'feature_addition':
                suggestions.append("Consider adding tests for new functionality")
                suggestions.append("Update documentation if public API changed")
            elif change_type == 'bug_fix':
                suggestions.append("Add regression test to prevent future issues")
                suggestions.append("Consider if this affects other similar code")
            elif change_type == 'architecture_change':
                suggestions.append("Review impact on dependent modules")
                suggestions.append("Consider updating architecture documentation")
            
            # Complexity-based suggestions
            if complexity == 'high':
                suggestions.append("Consider breaking this into smaller commits")
                suggestions.append("Ensure comprehensive testing for complex changes")
            elif complexity == 'medium':
                suggestions.append("Review changes for potential side effects")
            
            # Common files suggestions
            if patterns.get('common_files'):
                suggestions.append(f"Similar changes often affect: {', '.join(patterns['common_files'][:3])}")
            
            return suggestions[:4]  # Limit to most relevant suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")
            return ["Review changes carefully before committing"]

    def should_split_commit(self, changes: List[Dict]) -> Optional[Dict]:
        """Determine if changes should be split into multiple commits"""
        try:
            # Analyze change types
            change_types = set()
            file_types = set()
            
            for change in changes:
                filepath = change['filepath']
                
                # Categorize by file type
                if 'test' in filepath.lower():
                    file_types.add('test')
                elif filepath.endswith(('.py', '.js', '.ts')):
                    file_types.add('code')
                elif filepath.endswith(('.md', '.txt', '.rst')):
                    file_types.add('docs')
                elif filepath.endswith(('.json', '.yml', '.yaml', '.toml')):
                    file_types.add('config')
                
                # Categorize by semantic changes
                if change.get('semantic_changes'):
                    sc = change['semantic_changes']
                    if sc.get('functions_added') or sc.get('classes_added'):
                        change_types.add('feature')
                    elif sc.get('functions_removed') or sc.get('classes_removed'):
                        change_types.add('removal')
                    elif sc.get('functions_modified'):
                        change_types.add('modification')
            
            # Suggest split if mixing different types
            if len(file_types) > 2 or len(change_types) > 1:
                return {
                    'should_split': True,
                    'reason': f"Mixed change types: {', '.join(change_types)} across {', '.join(file_types)}",
                    'suggested_groups': self._suggest_commit_groups(changes, file_types, change_types)
                }
            
            return {'should_split': False}
            
        except Exception as e:
            logger.error(f"Failed to analyze commit split: {e}")
            return {'should_split': False, 'error': str(e)}

    def _suggest_commit_groups(self, changes: List[Dict], file_types: set, 
                              change_types: set) -> List[Dict]:
        """Suggest how to group changes into commits"""
        groups = []
        
        try:
            # Group by file type first
            type_groups = {'test': [], 'code': [], 'docs': [], 'config': []}
            
            for change in changes:
                filepath = change['filepath']
                if 'test' in filepath.lower():
                    type_groups['test'].append(change)
                elif filepath.endswith(('.py', '.js', '.ts')):
                    type_groups['code'].append(change)
                elif filepath.endswith(('.md', '.txt', '.rst')):
                    type_groups['docs'].append(change)
                elif filepath.endswith(('.json', '.yml', '.yaml', '.toml')):
                    type_groups['config'].append(change)
            
            # Create commit groups
            for group_type, group_changes in type_groups.items():
                if group_changes:
                    groups.append({
                        'type': group_type,
                        'files': [c['filepath'] for c in group_changes],
                        'suggested_message': self._suggest_group_message(group_type, group_changes)
                    })
            
            return groups
            
        except Exception as e:
            logger.error(f"Failed to suggest commit groups: {e}")
            return []

    def _suggest_group_message(self, group_type: str, changes: List[Dict]) -> str:
        """Suggest commit message for a group of changes"""
        try:
            if group_type == 'test':
                return f"test: add tests for {len(changes)} components"
            elif group_type == 'docs':
                return f"docs: update documentation ({len(changes)} files)"
            elif group_type == 'config':
                return f"chore: update configuration files"
            else:
                # Analyze semantic changes for code
                functions_added = sum(len(c.get('semantic_changes', {}).get('functions_added', [])) 
                                    for c in changes)
                classes_added = sum(len(c.get('semantic_changes', {}).get('classes_added', [])) 
                                  for c in changes)
                
                if functions_added > 0:
                    return f"feat: add {functions_added} new functions"
                elif classes_added > 0:
                    return f"feat: add {classes_added} new classes"
                else:
                    return f"refactor: update {len(changes)} files"
                    
        except Exception as e:
            logger.error(f"Failed to suggest group message: {e}")
            return f"update: modify {group_type} files"