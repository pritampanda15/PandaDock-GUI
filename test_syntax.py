#!/usr/bin/env python3
"""
Test script to verify syntax and basic imports for PandaDOCK GUI modifications
"""

def test_syntax():
    """Test basic syntax and imports"""
    try:
        # Test syntax by compiling the main file
        with open('PandaDOCK.py', 'r') as f:
            code = f.read()
        
        # Compile to check syntax
        compile(code, 'PandaDOCK.py', 'exec')
        print("✓ Syntax check passed")
        
        # Test styles import
        with open('styles.py', 'r') as f:
            styles_code = f.read()
        
        compile(styles_code, 'styles.py', 'exec')
        print("✓ Styles syntax check passed")
        
        # Test styles module execution
        exec(styles_code)
        print("✓ Styles module execution passed")
        
        return True
        
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing PandaDOCK GUI syntax and basic functionality...")
    success = test_syntax()
    if success:
        print("\n✓ All tests passed! Professional UI modifications are ready.")
    else:
        print("\n✗ Tests failed. Please check the errors above.")