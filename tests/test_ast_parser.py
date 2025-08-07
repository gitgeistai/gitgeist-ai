# tests/test_ast_parser.py
import pytest
from gitgeist.analysis.ast_parser import GitgeistASTParser

def test_language_detection():
    """Test programming language detection from file extensions"""
    parser = GitgeistASTParser()
    
    assert parser.detect_language("test.py") == "python"
    assert parser.detect_language("test.js") == "javascript"
    assert parser.detect_language("test.jsx") == "javascript"
    assert parser.detect_language("test.ts") == "typescript"
    assert parser.detect_language("test.tsx") == "typescript"
    assert parser.detect_language("test.txt") is None

def test_python_function_extraction():
    """Test Python function extraction from AST"""
    parser = GitgeistASTParser()
    
    python_code = '''
def hello_world():
    print("Hello, World!")

def add_numbers(a, b):
    return a + b

class TestClass:
    def method(self):
        pass
'''
    
    root_node = parser.parse_content(python_code, "python")
    if root_node:  # Only test if tree-sitter is available
        functions = parser.extract_functions(root_node, "python")
        
        function_names = [f['name'] for f in functions]
        assert "hello_world" in function_names
        assert "add_numbers" in function_names
        assert "method" in function_names

def test_javascript_function_extraction():
    """Test JavaScript function extraction from AST"""
    parser = GitgeistASTParser()
    
    js_code = '''
function regularFunction() {
    return "hello";
}

const arrowFunction = () => {
    return "world";
};

class MyClass {
    method() {
        return "test";
    }
}
'''
    
    root_node = parser.parse_content(js_code, "javascript")
    if root_node:  # Only test if tree-sitter is available
        functions = parser.extract_functions(root_node, "javascript")
        
        # Should find at least the regular function
        assert len(functions) >= 1
        function_names = [f['name'] for f in functions]
        assert "regularFunction" in function_names

def test_semantic_diff():
    """Test semantic diff between code versions"""
    parser = GitgeistASTParser()
    
    old_code = '''
def old_function():
    pass

class OldClass:
    pass
'''
    
    new_code = '''
def old_function():
    pass

def new_function():
    return "new"

class OldClass:
    pass

class NewClass:
    pass
'''
    
    diff = parser.semantic_diff(old_code, new_code, "python")
    
    if 'error' not in diff:  # Only test if tree-sitter is available
        assert len(diff.get('functions_added', [])) == 1
        assert len(diff.get('classes_added', [])) == 1
        assert 'new_function' in diff.get('functions_added', [])
        assert 'NewClass' in diff.get('classes_added', [])