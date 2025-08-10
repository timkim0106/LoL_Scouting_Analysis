#!/usr/bin/env python3
"""Simple test for Gwen implementation."""

from lol_analytics.core import ChampionAnalyzer
from lol_analytics.models.item import NASHORS_TOOTH, RIFTMAKER, LICH_BANE

def test_gwen_basic():
    """Basic test of Gwen damage calculations."""
    print("Testing Gwen implementation...")
    
    try:
        analyzer = ChampionAnalyzer()
        gwen = analyzer.get_champion("Gwen")
        print(f"✓ Successfully loaded Gwen")
        
        # Test basic stats
        stats_13 = gwen.get_stats_at_level(13)
        print(f"✓ Level 13 stats: {stats_13.health} HP, {stats_13.attack_damage} AD")
        
        # Test build comparison
        builds = {
            "Nashor's + Riftmaker": [NASHORS_TOOTH, RIFTMAKER],
            "Nashor's + Lich Bane": [NASHORS_TOOTH, LICH_BANE]
        }
        
        combo = ['A', 'Q', 'A', 'E', 'A']  # Combo with abilities and autos
        
        print("\nBuild Comparison at Level 13:")
        print("-" * 40)
        
        for build_name, items in builds.items():
            result = gwen.calculate_combo_damage(
                combo=combo,
                level=13,
                items=items,
                target_armor=100,
                target_mr=60,
                target_health=3000
            )
            
            print(f"{build_name}:")
            print(f"  Total Damage: {result['total_dealt']:.1f}")
            print(f"  Magic Damage: {result['magic_dealt']:.1f}")
            print(f"  Thousand Cuts: {result['special_effects']['thousand_cuts_damage']:.1f}")
            print(f"  Nashor's On-Hit: {result['special_effects'].get('nashors_on_hit_damage', 0):.1f}")
            print(f"  Lich Bane Spellblade: {result['special_effects'].get('lich_bane_spellblade_damage', 0):.1f}")
            print(f"  Healing: {result['special_effects']['thousand_cuts_healing']:.1f}")
            print()
        
        print("✓ Gwen test completed successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gwen_basic()