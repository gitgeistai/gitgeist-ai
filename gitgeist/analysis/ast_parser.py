# gitgeist/analysis/ast_parser.py
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import tree_sitter_javascript as tsjs
    import tree_sitter_python as tspython
    import tree_sitter_typescript as tsts
    from tree_sitter import Language, Node, Parser

    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

    # Create dummy Node class for type hints
    class Node:
        pass

    print(
        "⚠️  Tree-sitter not available. Install with: pip install tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript"
    )

from gitgeist.utils.exceptions import ParseError
from gitgeist.utils.logger import get_logger

logger = get_logger(__name__)


class GitgeistASTParser:
    """AST parser for multi-language semantic analysis"""

    def __init__(self):
        self.languages = {}
        self.parsers = {}

        if TREE_SITTER_AVAILABLE:
            try:
                self.languages = {
                    "python": Language(tspython.language()),
                    "javascript": Language(tsjs.language()),
                    "typescript": Language(tsts.language_typescript()),
                }
                self._init_parsers()
                logger.info(
                    f"Tree-sitter initialized with languages: {list(self.languages.keys())}"
                )
            except Exception as e:
                logger.error(f"Failed to initialize tree-sitter: {e}")
                self.languages = {}
        else:
            logger.warning("Tree-sitter not available - semantic analysis disabled")

    def _init_parsers(self):
        """Initialize parsers for each supported language"""
        for lang_name, language in self.languages.items():
            parser = Parser()
            parser.language = language
            self.parsers[lang_name] = parser

    def detect_language(self, filepath: str) -> Optional[str]:
        """Detect programming language from file extension"""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
        }

        suffix = Path(filepath).suffix.lower()
        return ext_map.get(suffix)

    def parse_file(self, filepath: str) -> Optional[Tuple[str, Node]]:
        """Parse a file and return (language, root_node)"""
        if not TREE_SITTER_AVAILABLE:
            return None

        language = self.detect_language(filepath)
        if not language or language not in self.parsers:
            return None

        try:
            with open(filepath, "rb") as f:
                code = f.read()

            tree = self.parsers[language].parse(code)
            return (language, tree.root_node)
        except Exception as e:
            logger.error(f"Error parsing {filepath}: {e}")
            return None

    def parse_content(self, content: str, language: str) -> Optional[Node]:
        """Parse content string and return root node"""
        if not TREE_SITTER_AVAILABLE or language not in self.parsers:
            return None

        try:
            tree = self.parsers[language].parse(content.encode("utf-8"))
            return tree.root_node
        except Exception as e:
            logger.error(f"Error parsing content: {e}")
            return None

    def extract_functions(self, node: Node, language: str) -> List[Dict]:
        """Extract function definitions from AST"""
        functions = []

        if language == "python":
            if node.type == "function_definition":
                name_node = node.child_by_field_name("name")
                if name_node:
                    functions.append(
                        {
                            "name": name_node.text.decode("utf-8"),
                            "start_line": node.start_point[0] + 1,
                            "end_line": node.end_point[0] + 1,
                            "type": "function",
                        }
                    )

        elif language in ["javascript", "typescript"]:
            if node.type in [
                "function_declaration",
                "arrow_function",
                "function_expression",
            ]:
                name = self._extract_js_function_name(node)
                if name:
                    functions.append(
                        {
                            "name": name,
                            "start_line": node.start_point[0] + 1,
                            "end_line": node.end_point[0] + 1,
                            "type": "function",
                        }
                    )

        # Recursively check children
        for child in node.children:
            functions.extend(self.extract_functions(child, language))

        return functions

    def _extract_js_function_name(self, node: Node) -> Optional[str]:
        """Extract function name from JavaScript/TypeScript function node"""
        if node.type == "function_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                return name_node.text.decode("utf-8")
        return "anonymous"

    def extract_classes(self, node: Node, language: str) -> List[Dict]:
        """Extract class definitions from AST"""
        classes = []

        if language == "python":
            if node.type == "class_definition":
                name_node = node.child_by_field_name("name")
                if name_node:
                    classes.append(
                        {
                            "name": name_node.text.decode("utf-8"),
                            "start_line": node.start_point[0] + 1,
                            "end_line": node.end_point[0] + 1,
                            "type": "class",
                        }
                    )

        elif language in ["javascript", "typescript"]:
            if node.type == "class_declaration":
                name_node = node.child_by_field_name("name")
                if name_node:
                    classes.append(
                        {
                            "name": name_node.text.decode("utf-8"),
                            "start_line": node.start_point[0] + 1,
                            "end_line": node.end_point[0] + 1,
                            "type": "class",
                        }
                    )

        # Recursively check children
        for child in node.children:
            classes.extend(self.extract_classes(child, language))

        return classes

    def extract_imports(self, node: Node, language: str) -> List[Dict]:
        """Extract import statements from AST"""
        imports = []

        if language == "python":
            if node.type in ["import_statement", "import_from_statement"]:
                import_text = node.text.decode("utf-8")
                imports.append(
                    {
                        "statement": import_text,
                        "line": node.start_point[0] + 1,
                        "type": "import",
                    }
                )

        elif language in ["javascript", "typescript"]:
            if node.type == "import_statement":
                import_text = node.text.decode("utf-8")
                imports.append(
                    {
                        "statement": import_text,
                        "line": node.start_point[0] + 1,
                        "type": "import",
                    }
                )

        # Recursively check children
        for child in node.children:
            imports.extend(self.extract_imports(child, language))

        return imports

    def analyze_file_structure(self, filepath: str) -> Optional[Dict]:
        """Analyze file structure and return summary"""
        result = self.parse_file(filepath)
        if not result:
            return None

        language, root_node = result

        return {
            "filepath": filepath,
            "language": language,
            "functions": self.extract_functions(root_node, language),
            "classes": self.extract_classes(root_node, language),
            "imports": self.extract_imports(root_node, language),
            "total_lines": root_node.end_point[0] + 1,
        }

    def analyze_content_structure(self, content: str, language: str) -> Optional[Dict]:
        """Analyze content structure from string"""
        root_node = self.parse_content(content, language)
        if not root_node:
            return None

        return {
            "language": language,
            "functions": self.extract_functions(root_node, language),
            "classes": self.extract_classes(root_node, language),
            "imports": self.extract_imports(root_node, language),
            "total_lines": root_node.end_point[0] + 1,
        }

    def semantic_diff(self, old_content: str, new_content: str, language: str) -> Dict:
        """Compare two versions of code at semantic level"""
        if not TREE_SITTER_AVAILABLE or language not in self.parsers:
            return {"error": f"Language {language} not supported"}

        # Analyze both versions
        old_analysis = self.analyze_content_structure(old_content, language)
        new_analysis = self.analyze_content_structure(new_content, language)

        if not old_analysis or not new_analysis:
            return {"error": "Failed to parse content"}

        # Compare structures
        return self._compare_structures(old_analysis, new_analysis)

    def _compare_structures(self, old: Dict, new: Dict) -> Dict:
        """Compare two file structures for semantic changes"""
        changes = {
            "functions_added": [],
            "functions_removed": [],
            "functions_modified": [],
            "classes_added": [],
            "classes_removed": [],
            "classes_modified": [],
            "imports_changed": False,
        }

        # Compare functions
        old_funcs = {f["name"]: f for f in old.get("functions", [])}
        new_funcs = {f["name"]: f for f in new.get("functions", [])}

        changes["functions_added"] = list(set(new_funcs.keys()) - set(old_funcs.keys()))
        changes["functions_removed"] = list(
            set(old_funcs.keys()) - set(new_funcs.keys())
        )

        # Check for modified functions (line number changes as proxy)
        for name in set(old_funcs.keys()) & set(new_funcs.keys()):
            if (
                old_funcs[name]["start_line"] != new_funcs[name]["start_line"]
                or old_funcs[name]["end_line"] != new_funcs[name]["end_line"]
            ):
                changes["functions_modified"].append(name)

        # Compare classes
        old_classes = {c["name"]: c for c in old.get("classes", [])}
        new_classes = {c["name"]: c for c in new.get("classes", [])}

        changes["classes_added"] = list(
            set(new_classes.keys()) - set(old_classes.keys())
        )
        changes["classes_removed"] = list(
            set(old_classes.keys()) - set(new_classes.keys())
        )

        # Compare imports (simple check)
        old_imports = set(i["statement"] for i in old.get("imports", []))
        new_imports = set(i["statement"] for i in new.get("imports", []))
        changes["imports_changed"] = old_imports != new_imports

        return changes


# Usage example
if __name__ == "__main__":
    parser = GitgeistASTParser()

    # Test if working
    if TREE_SITTER_AVAILABLE:
        print("✅ Tree-sitter initialized successfully")
        print(f"Supported languages: {list(parser.languages.keys())}")
    else:
        print("❌ Tree-sitter not available")
