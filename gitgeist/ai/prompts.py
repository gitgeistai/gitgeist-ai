# gitgeist/ai/prompts.py

COMMIT_PROMPTS = {
    'conventional': """You are an expert Git commit message generator. Generate a conventional commit message based on the semantic code changes below.

RULES:
- Use conventional commit format: type(scope): description
- Types: feat (new features), fix (bug fixes), refactor (code restructuring), docs (documentation), style (formatting), test (testing), chore (maintenance)
- Keep first line under 72 characters
- Be specific about WHAT changed, not just WHERE
- Focus on the most significant change if multiple types exist

CODE CHANGES ANALYSIS:
- Total files changed: {total_files} ({code_files} code files)
- Languages: {languages}
- Functions added: {functions_added} ({functions_added_list})
- Functions removed: {functions_removed}
- Functions modified: {functions_modified}
- Classes added: {classes_added} ({classes_added_list})
- Classes removed: {classes_removed}

FILE DETAILS:
{file_changes}

TEXT DIFF STATS:
- Lines added: +{insertions}
- Lines removed: -{deletions}

Generate ONLY the commit message, no explanation:""",

    'semantic': """Generate a semantic commit message that clearly describes the code changes. Focus on the functional impact, not just file changes.

ANALYSIS:
- Files: {total_files} changed ({code_files} code files)
- Languages: {languages}
- New functions: {functions_added} ({functions_added_list})
- Removed functions: {functions_removed}
- Modified functions: {functions_modified}
- New classes: {classes_added} ({classes_added_list})
- Removed classes: {classes_removed}

CHANGES BY FILE:
{file_changes}

STATS: +{insertions}/-{deletions} lines

Write a clear, action-oriented commit message that explains what the code now does differently:""",

    'default': """Generate a clear, concise Git commit message for these changes:

Summary:
- {total_files} files changed ({code_files} code files)
- {functions_added} functions added, {functions_removed} removed
- {classes_added} classes added, {classes_removed} removed
- Languages: {languages}

Files modified:
{file_changes}

Changes: +{insertions}/-{deletions} lines

Commit message:"""
}

SYSTEM_PROMPTS = {
    'commit_generator': """You are GitGeist, an AI assistant specialized in generating meaningful Git commit messages. 

Your role:
- Analyze semantic code changes (functions, classes, imports)
- Generate conventional or semantic commit messages
- Focus on functional impact, not just file modifications
- Be concise but descriptive
- Never include explanations, only the commit message

Always respond with just the commit message, nothing else.""",

    'code_analyzer': """You are a code analysis expert. Your role is to understand code changes at a semantic level and explain their functional impact.

Focus on:
- What new functionality was added
- What behavior changed
- What was refactored or reorganized
- Impact on the overall system

Be precise and technical, but accessible."""
}

# Example commit message patterns
COMMIT_EXAMPLES = {
    'new_feature': "feat(auth): add user login with JWT authentication",
    'bug_fix': "fix(api): resolve null pointer exception in user service",
    'refactor': "refactor(database): extract connection pooling to separate module",
    'documentation': "docs(readme): add installation and usage instructions",
    'test': "test(auth): add unit tests for password validation",
    'chore': "chore(deps): update dependencies to latest versions"
}

def get_commit_type_from_changes(changes: dict) -> str:
    """Determine commit type based on semantic changes"""
    
    if changes.get('functions_added') or changes.get('classes_added'):
        return 'feat'
    elif changes.get('functions_removed') or changes.get('classes_removed'):
        return 'refactor'
    elif changes.get('functions_modified') or changes.get('classes_modified'):
        return 'refactor'
    elif changes.get('imports_changed'):
        return 'refactor'
    else:
        return 'chore'

def format_function_list(functions: list, max_items: int = 3) -> str:
    """Format function list for prompts"""
    if not functions:
        return 'none'
    
    if len(functions) <= max_items:
        return ', '.join(functions)
    else:
        return f"{', '.join(functions[:max_items])}, +{len(functions) - max_items} more"