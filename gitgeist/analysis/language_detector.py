# gitgeist/analysis/language_detector.py
from pathlib import Path
from typing import Dict, Optional, Set

from gitgeist.utils.logger import get_logger

logger = get_logger(__name__)


class LanguageDetector:
    """Detects programming languages from file extensions and content"""

    # Language mappings
    EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.kt': 'kotlin',
        '.kts': 'kotlin',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.cs': 'csharp',
        '.swift': 'swift',
        '.scala': 'scala',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'bash',
        '.sql': 'sql',
        '.r': 'r',
        '.R': 'r',
        '.lua': 'lua',
        '.dart': 'dart',
        '.elm': 'elm',
        '.ex': 'elixir',
        '.exs': 'elixir',
        '.clj': 'clojure',
        '.cljs': 'clojure',
        '.hs': 'haskell',
        '.ml': 'ocaml',
        '.fs': 'fsharp',
        '.vb': 'vbnet',
        '.pl': 'perl',
        '.pm': 'perl',
        '.m': 'objective-c',
        '.mm': 'objective-c',
    }

    # Shebang patterns
    SHEBANGS = {
        'python': ['#!/usr/bin/env python', '#!/usr/bin/python'],
        'bash': ['#!/bin/bash', '#!/bin/sh', '#!/usr/bin/env bash'],
        'ruby': ['#!/usr/bin/env ruby', '#!/usr/bin/ruby'],
        'node': ['#!/usr/bin/env node', '#!/usr/bin/node'],
    }

    # Tree-sitter supported languages
    TREE_SITTER_SUPPORTED = {
        'python', 'javascript', 'typescript', 'java', 'go', 'rust',
        'cpp', 'c', 'ruby', 'php', 'bash', 'sql'
    }

    @classmethod
    def detect_language(cls, filepath: str, content: str = None) -> Optional[str]:
        """Detect programming language from file path and content"""
        path = Path(filepath)
        
        # Try extension first
        language = cls.EXTENSIONS.get(path.suffix.lower())
        if language:
            return language
        
        # Check shebang if no extension match
        if content:
            language = cls._detect_from_shebang(content)
            if language:
                return language
        
        # Special cases
        if path.name.lower() in ['makefile', 'dockerfile']:
            return path.name.lower()
        
        if path.name.lower() in ['package.json', 'tsconfig.json']:
            return 'json'
        
        return None

    @classmethod
    def _detect_from_shebang(cls, content: str) -> Optional[str]:
        """Detect language from shebang line"""
        if not content.startswith('#!'):
            return None
        
        first_line = content.split('\n')[0].lower()
        
        for language, shebangs in cls.SHEBANGS.items():
            for shebang in shebangs:
                if shebang in first_line:
                    return language
        
        return None

    @classmethod
    def is_supported_by_tree_sitter(cls, language: str) -> bool:
        """Check if language is supported by Tree-sitter"""
        return language in cls.TREE_SITTER_SUPPORTED

    @classmethod
    def get_supported_languages(cls) -> Set[str]:
        """Get all supported languages"""
        return set(cls.EXTENSIONS.values()) | set(cls.SHEBANGS.keys())

    @classmethod
    def get_language_stats(cls, filepaths: list) -> Dict[str, int]:
        """Get language statistics for a list of files"""
        stats = {}
        
        for filepath in filepaths:
            language = cls.detect_language(filepath)
            if language:
                stats[language] = stats.get(language, 0) + 1
        
        return stats

    @classmethod
    def is_code_file(cls, filepath: str) -> bool:
        """Check if file is a code file"""
        language = cls.detect_language(filepath)
        return language is not None

    @classmethod
    def get_file_category(cls, filepath: str) -> str:
        """Categorize file type"""
        path = Path(filepath)
        language = cls.detect_language(filepath)
        
        if language:
            return 'code'
        
        # Documentation files
        if path.suffix.lower() in ['.md', '.rst', '.txt', '.adoc']:
            return 'docs'
        
        # Configuration files
        if path.suffix.lower() in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf']:
            return 'config'
        
        # Test files
        if 'test' in path.name.lower() or path.name.startswith('test_'):
            return 'test'
        
        # Build files
        if path.name.lower() in ['makefile', 'dockerfile', 'build.gradle', 'pom.xml']:
            return 'build'
        
        return 'other'