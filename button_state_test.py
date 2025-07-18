#!/usr/bin/env python3
"""
Button State Test for PandaDOCK GUI
Verifies that button states are correctly configured
"""

def test_button_states():
    """Test button enabling/disabling configuration"""
    
    print("PandaDOCK Button State Configuration Test")
    print("=" * 45)
    
    try:
        # Read the main file to check button state configuration
        with open('PandaDOCK.py', 'r') as f:
            content = f.read()
        
        # Check button state settings
        state_checks = [
            ("Start button enabled", "self.start_button.setEnabled(True)" in content),
            ("Ligand button disabled", "self.ligand_button.setEnabled(False)" in content),
            ("Protein button disabled", "self.protein_button.setEnabled(False)" in content),
            ("Binding site button disabled", "self.binding_site_button.setEnabled(False)" in content),
            ("Run button disabled", "self.run_button.setEnabled(False)" in content),
            ("Results button disabled", "self.results_button.setEnabled(False)" in content),
        ]
        
        print("Initial Button State Checks:")
        all_states_correct = True
        for check_name, result in state_checks:
            status = "✓" if result else "✗"
            print(f"  {status} {check_name}")
            if not result:
                all_states_correct = False
        
        # Check styling configuration
        from styles import MAIN_COLORS, PROFESSIONAL_THEME
        
        styling_checks = [
            ("Enabled button background", f"{MAIN_COLORS['primary']}" in PROFESSIONAL_THEME),
            ("Disabled button background", f"{MAIN_COLORS['surface']}" in PROFESSIONAL_THEME),
            ("Enabled button text", "color: white !important" in PROFESSIONAL_THEME),
            ("Disabled button text", f"color: {MAIN_COLORS['text']} !important" in PROFESSIONAL_THEME),
        ]
        
        print("\nButton Styling Configuration:")
        all_styling_correct = True
        for check_name, result in styling_checks:
            status = "✓" if result else "✗"
            print(f"  {status} {check_name}")
            if not result:
                all_styling_correct = False
        
        # Expected appearance
        print(f"\nExpected Button Appearance:")
        print(f"  🎯 Initialize Session:")
        print(f"     • State: ENABLED")
        print(f"     • Background: Blue gradient ({MAIN_COLORS['primary']})")
        print(f"     • Text: White")
        print(f"     • Border: Dark blue")
        print(f"  🎯 All other buttons:")
        print(f"     • State: DISABLED") 
        print(f"     • Background: Light gray ({MAIN_COLORS['surface']})")
        print(f"     • Text: Dark gray ({MAIN_COLORS['text']})")
        print(f"     • Border: Light gray")
        
        # Troubleshooting
        print(f"\nTroubleshooting Notes:")
        print(f"  💡 If Initialize button shows white text on light background:")
        print(f"     - Button may be getting focus styling")
        print(f"     - CSS specificity might need adjustment")
        print(f"     - Button state refresh may be needed")
        
        if all_states_correct and all_styling_correct:
            print("\n🎉 All button state tests PASSED!")
            print("Initialize button should show blue background with white text.")
        else:
            print("\n⚠️ Some button state tests failed.")
            
        return all_states_correct and all_styling_correct
        
    except Exception as e:
        print(f"Error during button state test: {e}")
        return False

if __name__ == "__main__":
    test_button_states()