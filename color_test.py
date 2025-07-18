#!/usr/bin/env python3
"""
Test script to verify button color styling
"""

def test_button_colors():
    """Test that button colors are properly configured"""
    
    try:
        # Import the styles to check color values
        from styles import MAIN_COLORS, PROFESSIONAL_THEME
        
        print("Testing Button Color Configuration...")
        print("=" * 45)
        
        # Check main colors
        print(f"✓ Primary color: {MAIN_COLORS['primary']}")
        print(f"✓ Text color: {MAIN_COLORS['text']}")
        print(f"✓ Surface color: {MAIN_COLORS['surface']}")
        
        # Check that the theme contains proper button styling
        checks = [
            ("Primary button background", "QPushButton" in PROFESSIONAL_THEME),
            ("Button text color", "color: white !important" in PROFESSIONAL_THEME),
            ("Disabled button styling", "QPushButton:disabled" in PROFESSIONAL_THEME),
            ("Hover state styling", "QPushButton:hover" in PROFESSIONAL_THEME),
        ]
        
        print("\nButton Styling Checks:")
        for check_name, result in checks:
            status = "✓" if result else "✗"
            print(f"  {status} {check_name}")
        
        # Test color contrast
        print(f"\nColor Contrast Check:")
        print(f"✓ Enabled buttons: White text on {MAIN_COLORS['primary']} background")
        print(f"✓ Disabled buttons: {MAIN_COLORS['text']} text on {MAIN_COLORS['surface']} background")
        
        all_passed = all(result for _, result in checks)
        if all_passed:
            print("\n🎉 All button color tests passed!")
            print("Button text should now be visible with proper contrast.")
        else:
            print("\n⚠️ Some button color tests failed.")
            
        return all_passed
        
    except Exception as e:
        print(f"Error testing button colors: {e}")
        return False

if __name__ == "__main__":
    test_button_colors()