#!/usr/bin/env python3
"""
Layout verification script for PandaDOCK GUI button fixes
"""

def verify_layout_fixes():
    """Verify that layout fixes have been properly implemented"""
    
    print("Verifying PandaDOCK GUI Layout Fixes...")
    print("=" * 50)
    
    fixes_verified = []
    
    try:
        # Read the main file
        with open('PandaDOCK.py', 'r') as f:
            content = f.read()
        
        # Check 1: Redundant button creation removed
        if 'buttons = [' not in content or content.count('("🚀 Initialize"') == 0:
            fixes_verified.append("✓ Redundant button creation code removed")
        else:
            fixes_verified.append("✗ Redundant button creation code still present")
        
        # Check 2: Dock widget height increased
        if 'setFixedSize(320, 550)' in content:
            fixes_verified.append("✓ Dock widget height increased to accommodate 6 buttons")
        else:
            fixes_verified.append("✗ Dock widget height not properly increased")
        
        # Check 3: Professional color scheme applied
        if 'MAIN_COLORS[' in content and content.count('MAIN_COLORS[') > 5:
            fixes_verified.append("✓ Professional color scheme consistently applied")
        else:
            fixes_verified.append("✗ Professional color scheme not consistently applied")
        
        # Check 4: Results button added
        if 'self.results_button' in content and 'View Results' in content:
            fixes_verified.append("✓ Results viewing button added")
        else:
            fixes_verified.append("✗ Results viewing button not found")
        
        # Check 5: Layout spacing optimized
        if 'setSpacing(4)' in content and 'setContentsMargins(8, 8, 8, 8)' in content:
            fixes_verified.append("✓ Layout spacing optimized for better fit")
        else:
            fixes_verified.append("✗ Layout spacing not optimized")
        
        # Check 6: Button height reduced for better fit
        if 'setFixedHeight(38)' in content:
            fixes_verified.append("✓ Button height optimized")
        else:
            fixes_verified.append("✗ Button height not optimized")
        
        print("\nLayout Fix Verification Results:")
        for fix in fixes_verified:
            print(f"  {fix}")
        
        success_count = sum(1 for fix in fixes_verified if fix.startswith("✓"))
        total_count = len(fixes_verified)
        
        print(f"\nSummary: {success_count}/{total_count} fixes verified")
        
        if success_count == total_count:
            print("\n🎉 All layout fixes successfully implemented!")
            print("The button overlapping issue should now be resolved.")
            return True
        else:
            print(f"\n⚠️  {total_count - success_count} issues still need attention.")
            return False
            
    except Exception as e:
        print(f"Error during verification: {e}")
        return False

if __name__ == "__main__":
    verify_layout_fixes()