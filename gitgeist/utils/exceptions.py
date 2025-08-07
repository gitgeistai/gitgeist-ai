class GitgeistError(Exception):
    """Base exception for Gitgeist with user-friendly messages"""
    
    def __init__(self, message: str, suggestion: str = None):
        super().__init__(message)
        self.suggestion = suggestion


class GitError(GitgeistError):
    """Git operation failed"""
    pass


class LLMError(GitgeistError):
    """LLM generation failed"""
    pass


class AnalysisError(GitgeistError):
    """Code analysis errors"""
    pass


class ConfigurationError(GitgeistError):
    """Configuration related errors"""
    pass


class MemoryError(GitgeistError):
    """Memory/RAG system errors"""
    pass


class ValidationError(GitgeistError):
    """Input validation errors"""
    pass
