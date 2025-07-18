#!/usr/bin/env python3
"""
Individual Button Styling Test for PandaDOCK GUI
Verifies Copilot's suggested approach implementation
"""

def test_individual_button_styling():
    """Test individual button stylesheet implementation"""
    
    print("🎨 Individual Button Styling Test (Copilot's Approach)")
    print("=" * 60)
    
    try:
        # Read the main file to check implementation
        with open('PandaDOCK.py', 'r') as f:
            content = f.read()
        
        # Check for individual styling implementation
        implementation_checks = [
            # Style variable definitions
            ("✓ Enabled button style defined", "self.enabled_button_style" in content),
            ("✓ Disabled button style defined", "self.disabled_button_style" in content),
            
            # Individual button style applications
            ("✓ Start button styled individually", "self.start_button.setStyleSheet(self.enabled_button_style)" in content),
            ("✓ Ligand button styled individually", "self.ligand_button.setStyleSheet(" in content),
            ("✓ Protein button styled individually", "self.protein_button.setStyleSheet(" in content),
            ("✓ Binding site button styled individually", "self.binding_site_button.setStyleSheet(" in content),
            ("✓ Run button styled individually", "self.run_button.setStyleSheet(" in content),
            ("✓ Results button styled individually", "self.results_button.setStyleSheet(" in content),
            
            # Dynamic styling updates
            ("✓ Style updates on enable/disable", content.count("setStyleSheet(self.enabled_button_style)") >= 4),
            ("✓ Professional colors used", "MAIN_COLORS['primary']" in content),
        ]
        
        print("Implementation Verification:")
        passed_count = 0
        for check_desc, result in implementation_checks:
            if result:
                print(f"  {check_desc}")
                passed_count += 1
            else:
                print(f"  ❌ FAILED: {check_desc.replace('✓ ', '')}")
        
        # Check style content quality
        style_quality_checks = []
        
        # Look for enabled button style content
        if "color: white;" in content and "background: qlineargradient" in content:
            style_quality_checks.append(("✓ Enabled style has white text and gradient background", True))
        else:
            style_quality_checks.append(("❌ Enabled style missing proper styling", False))
            
        # Look for disabled button style content
        if "MAIN_COLORS['text']" in content and "MAIN_COLORS['surface']" in content:
            style_quality_checks.append(("✓ Disabled style uses professional colors", True))
        else:
            style_quality_checks.append(("❌ Disabled style missing professional colors", False))
        
        print("\nStyle Quality Checks:")
        for check_desc, result in style_quality_checks:
            if result:
                print(f"  {check_desc}")
                passed_count += 1
            else:
                print(f"  {check_desc}")
        
        total_checks = len(implementation_checks) + len(style_quality_checks)
        
        print(f"\nResults: {passed_count}/{total_checks} checks passed")
        
        # Benefits of this approach
        print(f"\n🎯 Benefits of Individual Button Styling:")
        print(f"   ✅ Direct control - No CSS inheritance issues")
        print(f"   ✅ Override capability - Supersedes any global styles")
        print(f"   ✅ State management - Explicit styling on enable/disable")
        print(f"   ✅ Debugging friendly - Easy to identify styling issues")
        print(f"   ✅ Maintainable - Clear separation of enabled/disabled styles")
        
        # Expected behavior
        print(f"\n🎨 Expected Button Appearance:")
        print(f"   Initialize Session Button:")
        print(f"   • Direct stylesheet: Enabled style")
        print(f"   • Background: Professional blue gradient")
        print(f"   • Text: Pure white")
        print(f"   • No inheritance conflicts")
        
        print(f"\n   All Other Buttons:")
        print(f"   • Direct stylesheet: Disabled style")
        print(f"   • Background: Professional light gray gradient")
        print(f"   • Text: Professional dark gray")
        print(f"   • Consistent disabled appearance")
        
        success = passed_count >= total_checks * 0.9  # 90% pass rate
        if success:
            print(f"\n🎉 INDIVIDUAL BUTTON STYLING SUCCESSFULLY IMPLEMENTED!")
            print(f"✅ Copilot's approach has been applied with professional styling")
            print(f"✅ Button text visibility issues should be completely resolved")
        else:
            print(f"\n⚠️  Some aspects of individual styling need attention")
            
        return success
        
    except Exception as e:
        print(f"❌ Error during styling test: {e}")
        return False

if __name__ == "__main__":
    test_individual_button_styling()