class GitgeistError(Exception):
    """Base exception for Gitgeist"""

    pass


class GitError(GitgeistError):
    """Git operation failed"""

    pass


class LLMError(GitgeistError):
    """LLM generation failed"""

    pass


class ParseError(GitgeistError):
    """Code parsing failed"""

    pass


class ConfigError(GitgeistError):
    """Configuration error"""

    pass
