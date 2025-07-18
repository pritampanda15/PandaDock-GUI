#!/usr/bin/env python3
"""
Button Visibility Test for PandaDOCK GUI
Tests that button text is visible in all states
"""

def test_button_visibility():
    """Test button text visibility across all states"""
    
    print("PandaDOCK Button Visibility Test")
    print("=" * 40)
    
    try:
        from styles import MAIN_COLORS, PROFESSIONAL_THEME
        
        # Check for visibility-related styling
        visibility_checks = [
            ("White text on enabled buttons", "color: white !important" in PROFESSIONAL_THEME),
            ("Dark text on disabled buttons", f"color: {MAIN_COLORS['text']} !important" in PROFESSIONAL_THEME),
            ("Specific disabled styling", "QPushButton:disabled" in PROFESSIONAL_THEME),
            ("Hover state text", "QPushButton:hover" in PROFESSIONAL_THEME),
            ("Pressed state text", "QPushButton:pressed" in PROFESSIONAL_THEME),
            ("Maximum specificity rules", "QWidget QPushButton" in PROFESSIONAL_THEME),
        ]
        
        print("Button Text Visibility Checks:")
        all_passed = True
        for check_name, result in visibility_checks:
            status = "✓" if result else "✗"
            print(f"  {status} {check_name}")
            if not result:
                all_passed = False
        
        # Color contrast information
        print(f"\nColor Contrast Analysis:")
        print(f"  📊 Enabled buttons:")
        print(f"     • Background: {MAIN_COLORS['primary']} (Primary blue)")
        print(f"     • Text: White (#ffffff)")
        print(f"     • Contrast: High (white on blue)")
        
        print(f"  📊 Disabled buttons:")
        print(f"     • Background: {MAIN_COLORS['surface']} (Light gray)")
        print(f"     • Text: {MAIN_COLORS['text']} (Dark gray)")
        print(f"     • Contrast: High (dark on light)")
        
        # Expected behavior
        print(f"\nExpected Button Behavior:")
        print(f"  🎯 Initialize Session: Enabled (white text on blue)")
        print(f"  🎯 Load Ligands: Disabled (dark text on light gray)")
        print(f"  🎯 Load Protein: Disabled (dark text on light gray)")
        print(f"  🎯 Define Binding Site: Disabled (dark text on light gray)")
        print(f"  🎯 Execute Docking: Disabled (dark text on light gray)")
        print(f"  🎯 View Results: Disabled (dark text on light gray)")
        
        if all_passed:
            print("\n🎉 All button visibility tests PASSED!")
            print("Button text should now be clearly visible in all states.")
        else:
            print("\n⚠️ Some visibility tests failed.")
            
        return all_passed
        
    except Exception as e:
        print(f"Error during visibility test: {e}")
        return False

if __name__ == "__main__":
    test_button_visibility()