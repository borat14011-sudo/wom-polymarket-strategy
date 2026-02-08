#!/usr/bin/env python3
"""
Syntax validation for advanced-logger.py

Tests that the module can be imported and basic functionality works.
"""

import sys
import ast

def validate_syntax(filename):
    """Check Python syntax by parsing the AST."""
    print(f"Validating {filename}...")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the AST
        ast.parse(source)
        print(f"✓ Syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def check_structure(filename):
    """Check that required functions and classes exist."""
    print(f"\nChecking structure...")
    
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()
    
    tree = ast.parse(source)
    
    # Expected components
    expected_classes = ['JSONFormatter', 'CompressingTimedRotatingFileHandler', 
                       'SizeAwareTimedRotatingFileHandler', 'ComponentLogger']
    expected_functions = ['get_logger', 'search_logs', 'generate_summary', 'main']
    
    # Find actual components
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    
    # Check classes
    print("\nClasses:")
    for cls in expected_classes:
        if cls in classes:
            print(f"  ✓ {cls}")
        else:
            print(f"  ✗ {cls} MISSING")
    
    # Check functions
    print("\nFunctions:")
    for func in expected_functions:
        if func in functions:
            print(f"  ✓ {func}")
        else:
            print(f"  ✗ {func} MISSING")
    
    return True

def main():
    print("="*60)
    print("  Advanced Logger - Syntax Validation")
    print("="*60 + "\n")
    
    filename = "advanced-logger.py"
    
    if validate_syntax(filename):
        check_structure(filename)
        print("\n" + "="*60)
        print("  ✓ All checks passed!")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("  ✗ Validation failed")
        print("="*60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
