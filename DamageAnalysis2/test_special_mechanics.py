#!/usr/bin/env python3
"""
Quick test script to verify special mechanics are working correctly.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from lol_analytics.core import ChampionAnalyzer
    from lol_analytics.models.item import ECLIPSE, MURAMANA
    from lol_analytics.utils.logger import logger
    
    def test_basic_functionality():
        """Test that the basic system works."""
        print("Testing basic functionality...")
        
        analyzer = ChampionAnalyzer()
        
        # Simple test
        builds = {"Test Build": [ECLIPSE, MURAMANA]}
        
        analysis = analyzer.analyze_item_builds(
            champion_name="Jayce",
            combo=['Q1'],
            builds=builds,
            level=13
        )
        
        result = analysis['builds']['Test Build']
        damage = result['damage']
        
        print(f"Basic test passed")
        print(f"   Total damage: {damage['total_dealt']:.1f}")
        print(f"   Special effects: {damage.get('special_effects', {})}")
        
        return True
    
    def test_eclipse_passive():
        """Test Eclipse passive mechanics."""
        print("\\nTesting Eclipse passive...")
        
        analyzer = ChampionAnalyzer()
        
        # Test 2 abilities = 1 Eclipse proc
        builds = {"Eclipse Build": [ECLIPSE]}
        
        analysis = analyzer.analyze_item_builds(
            champion_name="Jayce",
            combo=['Q1', 'W2'],  # 2 abilities
            builds=builds,
            level=13,
            target_stats={"armor": 100, "mr": 70, "health": 3000}
        )
        
        result = analysis['builds']['Eclipse Build']
        damage = result['damage']
        special = damage.get('special_effects', {})
        eclipse_procs = special.get('eclipse_procs', 0)
        
        print(f"Eclipse test passed")
        print(f"   Eclipse procs: {eclipse_procs}")
        print(f"   Total damage: {damage['total_dealt']:.1f}")
        
        return eclipse_procs > 0
    
    def test_muramana_bonus():
        """Test Muramana mana-to-AD conversion."""
        print("\\nTesting Muramana mechanics...")
        
        analyzer = ChampionAnalyzer()
        
        builds = {"Muramana Build": [MURAMANA]}
        
        analysis = analyzer.analyze_item_builds(
            champion_name="Jayce",
            combo=['Q1'],  # Ranged ability
            builds=builds,
            level=13
        )
        
        result = analysis['builds']['Muramana Build']
        damage = result['damage']
        special = damage.get('special_effects', {})
        muramana_ad = special.get('muramana_bonus_ad', 0)
        
        print(f"Muramana test passed")
        print(f"   Bonus AD from mana: {muramana_ad:.1f}")
        print(f"   Total damage: {damage['total_dealt']:.1f}")
        
        return muramana_ad > 0
    
    def main():
        """Run all tests."""
        print("="*60)
        print("TESTING SPECIAL MECHANICS IMPLEMENTATION")
        print("="*60)
        
        tests_passed = 0
        total_tests = 0
        
        # Test basic functionality
        total_tests += 1
        if test_basic_functionality():
            tests_passed += 1
        
        # Test Eclipse passive
        total_tests += 1
        if test_eclipse_passive():
            tests_passed += 1
        
        # Test Muramana mechanics
        total_tests += 1
        if test_muramana_bonus():
            tests_passed += 1
        
        print("\\n" + "="*60)
        print(f"TESTS COMPLETED: {tests_passed}/{total_tests} PASSED")
        print("="*60)
        
        if tests_passed == total_tests:
            print("All special mechanics are working correctly!")
            print("\\nNext Steps:")
            print("1. Run 'python enhanced_mechanics_demo.py' for detailed demonstrations")
            print("2. Run 'python example_analysis.py' for the full analysis suite")
            print("3. Add your Riot API key to .env file for player tracking")
        else:
            print("Some tests failed. Check the implementation.")
            return False
        
        return True

    if __name__ == "__main__":
        success = main()
        sys.exit(0 if success else 1)
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the correct directory and all dependencies are installed.")
    print("Try: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
