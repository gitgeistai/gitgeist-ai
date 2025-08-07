# gitgeist/core/templates.py
from typing import Dict, List, Optional

from gitgeist.utils.logger import get_logger

logger = get_logger(__name__)


class CommitTemplateManager:
    """Manages commit message templates and formatting"""

    def __init__(self):
        self.templates = {
            "conventional": {
                "feature": "feat({scope}): {description}",
                "fix": "fix({scope}): {description}",
                "refactor": "refactor({scope}): {description}",
                "docs": "docs({scope}): {description}",
                "style": "style({scope}): {description}",
                "test": "test({scope}): {description}",
                "chore": "chore({scope}): {description}",
                "perf": "perf({scope}): {description}",
                "ci": "ci({scope}): {description}",
                "build": "build({scope}): {description}",
                "revert": "revert({scope}): {description}"
            },
            "semantic": {
                "feature": "Add {description}",
                "fix": "Fix {description}",
                "refactor": "Refactor {description}",
                "docs": "Update {description}",
                "style": "Format {description}",
                "test": "Test {description}",
                "chore": "Maintain {description}",
                "perf": "Optimize {description}",
                "ci": "Configure {description}",
                "build": "Build {description}",
                "revert": "Revert {description}"
            },
            "default": {
                "feature": "{description}",
                "fix": "{description}",
                "refactor": "{description}",
                "docs": "{description}",
                "style": "{description}",
                "test": "{description}",
                "chore": "{description}",
                "perf": "{description}",
                "ci": "{description}",
                "build": "{description}",
                "revert": "{description}"
            }
        }

    def get_template(self, style: str, commit_type: str) -> Optional[str]:
        """Get commit template for style and type"""
        if style not in self.templates:
            style = "conventional"
        
        if commit_type not in self.templates[style]:
            commit_type = "feature"
        
        return self.templates[style][commit_type]

    def format_commit_message(self, style: str, commit_type: str, 
                            description: str, scope: str = None) -> str:
        """Format commit message using template"""
        template = self.get_template(style, commit_type)
        
        # Handle scope
        if "{scope}" in template:
            if scope:
                template = template.replace("{scope}", scope)
            else:
                # Remove scope if not provided
                template = template.replace("({scope})", "").replace("{scope}", "")
        
        # Replace description
        message = template.replace("{description}", description)
        
        # Clean up extra spaces
        message = " ".join(message.split())
        
        return message

    def infer_commit_type(self, changes: Dict) -> str:
        """Infer commit type from semantic changes"""
        # Check for new features
        if (changes.get("functions_added") or 
            changes.get("classes_added") or
            changes.get("new_files")):
            return "feature"
        
        # Check for fixes
        if (changes.get("functions_removed") or 
            changes.get("bug_fixes") or
            "fix" in str(changes).lower()):
            return "fix"
        
        # Check for refactoring
        if (changes.get("functions_modified") or 
            changes.get("classes_modified") or
            changes.get("code_restructured")):
            return "refactor"
        
        # Check for documentation
        if changes.get("doc_files") or "docs" in str(changes).lower():
            return "docs"
        
        # Check for tests
        if changes.get("test_files") or "test" in str(changes).lower():
            return "test"
        
        # Check for configuration
        if changes.get("config_files"):
            return "chore"
        
        # Default to feature
        return "feature"

    def infer_scope(self, files_changed: List[str]) -> Optional[str]:
        """Infer scope from changed files"""
        if not files_changed:
            return None
        
        # Common scope patterns
        scope_patterns = {
            "api": ["api/", "routes/", "endpoints/"],
            "auth": ["auth/", "login/", "authentication/"],
            "db": ["database/", "models/", "migrations/"],
            "ui": ["ui/", "components/", "views/"],
            "core": ["core/", "lib/", "utils/"],
            "config": ["config/", "settings/", ".env"],
            "docs": ["docs/", "README", ".md"],
            "tests": ["test/", "tests/", "spec/"],
            "ci": [".github/", "ci/", "pipeline/"],
            "deps": ["package.json", "requirements.txt", "Cargo.toml"]
        }
        
        # Count matches for each scope
        scope_counts = {}
        for file_path in files_changed:
            file_lower = file_path.lower()
            for scope, patterns in scope_patterns.items():
                for pattern in patterns:
                    if pattern in file_lower:
                        scope_counts[scope] = scope_counts.get(scope, 0) + 1
        
        # Return most common scope
        if scope_counts:
            return max(scope_counts, key=scope_counts.get)
        
        # Try to infer from directory structure
        common_dirs = set()
        for file_path in files_changed:
            parts = file_path.split("/")
            if len(parts) > 1:
                common_dirs.add(parts[0])
        
        if len(common_dirs) == 1:
            return list(common_dirs)[0]
        
        return None

    def generate_description(self, changes: Dict, files_changed: List[str]) -> str:
        """Generate commit description from changes"""
        descriptions = []
        
        # Functions
        if changes.get("functions_added"):
            count = len(changes["functions_added"])
            if count == 1:
                descriptions.append(f"add {changes['functions_added'][0]} function")
            else:
                descriptions.append(f"add {count} new functions")
        
        if changes.get("functions_removed"):
            count = len(changes["functions_removed"])
            descriptions.append(f"remove {count} functions")
        
        if changes.get("functions_modified"):
            count = len(changes["functions_modified"])
            descriptions.append(f"update {count} functions")
        
        # Classes
        if changes.get("classes_added"):
            count = len(changes["classes_added"])
            if count == 1:
                descriptions.append(f"add {changes['classes_added'][0]} class")
            else:
                descriptions.append(f"add {count} new classes")
        
        # Files
        if not descriptions and files_changed:
            file_count = len(files_changed)
            if file_count == 1:
                descriptions.append(f"update {files_changed[0]}")
            else:
                descriptions.append(f"update {file_count} files")
        
        # Default
        if not descriptions:
            descriptions.append("update code")
        
        return descriptions[0]

    def create_commit_message(self, style: str, changes: Dict, 
                            files_changed: List[str]) -> str:
        """Create complete commit message from changes"""
        commit_type = self.infer_commit_type(changes)
        scope = self.infer_scope(files_changed)
        description = self.generate_description(changes, files_changed)
        
        return self.format_commit_message(style, commit_type, description, scope)

    def add_custom_template(self, style: str, templates: Dict[str, str]) -> None:
        """Add custom commit templates"""
        if style not in self.templates:
            self.templates[style] = {}
        
        self.templates[style].update(templates)
        logger.info(f"Added custom templates for style: {style}")

    def get_available_styles(self) -> List[str]:
        """Get list of available template styles"""
        return list(self.templates.keys())

    def get_available_types(self, style: str = "conventional") -> List[str]:
        """Get list of available commit types for a style"""
        if style not in self.templates:
            style = "conventional"
        
        return list(self.templates[style].keys())