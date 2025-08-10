#!/usr/bin/env python3
"""Comprehensive test suite for Gwen damage and healing calculations."""

from lol_analytics.core import ChampionAnalyzer
from lol_analytics.models.item import NASHORS_TOOTH, RIFTMAKER, LICH_BANE, ZHONYAS_HOURGLASS

def print_scenario(title: str, level: int, combo: list, target_hp: int, target_armor: int, target_mr: int):
    """Print scenario details."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Gwen Level: {level}")
    print(f"Combo: {' → '.join(combo)}")
    print(f"Target: {target_hp} HP, {target_armor} Armor, {target_mr} MR")
    print("-" * 60)

def print_build_results(build_name: str, items: list, result: dict, detailed: bool = True):
    """Print detailed build results."""
    damage = result
    special = damage.get('special_effects', {})
    
    item_names = " + ".join([item.name for item in items])
    total_cost = sum(item.cost for item in items)
    
    print(f"\n{build_name}: {item_names}")
    print(f"  Cost: {total_cost:,}g")
    print(f"  Total Damage: {damage['total_dealt']:.1f}")
    
    if detailed:
        print(f"  ├─ Base Damage: {damage['total_dealt'] - special.get('thousand_cuts_damage', 0) - special.get('nashors_on_hit_damage', 0) - special.get('lich_bane_spellblade_damage', 0):.1f}")
        print(f"  ├─ Thousand Cuts: {special.get('thousand_cuts_damage', 0):.1f} ({special.get('thousand_cuts_hits', 0)} hits)")
        print(f"  ├─ Nashor's On-Hit: {special.get('nashors_on_hit_damage', 0):.1f}")
        print(f"  └─ Lich Bane Spellblade: {special.get('lich_bane_spellblade_damage', 0):.1f}")
        
        print(f"  Total Healing: {special.get('total_healing', 0):.1f}")
        print(f"  ├─ Thousand Cuts: {special.get('thousand_cuts_healing', 0):.1f}")
        print(f"  └─ Omnivamp: {special.get('omnivamp_healing', 0):.1f}")
        
        print(f"  Damage per Gold: {damage['total_dealt']/total_cost:.3f}")

def test_basic_functionality():
    """Test basic Gwen implementation."""
    print("BASIC FUNCTIONALITY TEST")
    print("="*60)
    
    analyzer = ChampionAnalyzer()
    gwen = analyzer.get_champion("Gwen")
    
    # Test champion loading
    print(f"✓ Successfully loaded Gwen")
    
    # Test stats at different levels
    for level in [6, 11, 16]:
        stats = gwen.get_stats_at_level(level)
        print(f"✓ Level {level}: {stats.health:.0f} HP, {stats.attack_damage:.0f} AD, {stats.armor:.0f} Armor, {stats.magic_resist:.0f} MR")
    
    print("\n✓ Basic functionality test passed!")

def test_2_item_builds_vs_squishy():
    """Test 2-item builds against squishy target."""
    analyzer = ChampionAnalyzer()
    gwen = analyzer.get_champion("Gwen")
    
    builds = {
        "Sustain Build": [NASHORS_TOOTH, RIFTMAKER],
        "Burst Build": [NASHORS_TOOTH, LICH_BANE]
    }
    
    # Test scenario: Standard combo vs Squishy ADC
    level = 13
    combo = ['A', 'Q', 'A', 'E', 'A']  # Auto → Q (Snip) → Auto → E (Skip'n Slash) → Auto
    target_hp, target_armor, target_mr = 2200, 65, 35  # Typical ADC stats
    
    print_scenario("2-ITEM BUILDS vs SQUISHY ADC", level, combo, target_hp, target_armor, target_mr)
    
    results = {}
    for build_name, items in builds.items():
        result = gwen.calculate_combo_damage(
            combo=combo,
            level=level,
            items=items,
            target_armor=target_armor,
            target_mr=target_mr,
            target_health=target_hp
        )
        results[build_name] = result
        print_build_results(build_name, items, result)
    
    # Compare builds
    sustain_dmg = results["Sustain Build"]["total_dealt"]
    burst_dmg = results["Burst Build"]["total_dealt"]
    dmg_diff = burst_dmg - sustain_dmg
    
    sustain_heal = results["Sustain Build"]["special_effects"]["total_healing"]
    burst_heal = results["Burst Build"]["special_effects"]["total_healing"]
    heal_diff = sustain_heal - burst_heal
    
    print(f"\n📊 COMPARISON:")
    print(f"  Damage: Burst Build +{dmg_diff:.0f} damage ({dmg_diff/sustain_dmg*100:.1f}% more)")
    print(f"  Healing: Sustain Build +{heal_diff:.0f} healing ({heal_diff/burst_heal*100:.1f}% more)")

def test_2_item_builds_vs_bruiser():
    """Test 2-item builds against bruiser target."""
    analyzer = ChampionAnalyzer()
    gwen = analyzer.get_champion("Gwen")
    
    builds = {
        "Sustain Build": [NASHORS_TOOTH, RIFTMAKER],
        "Burst Build": [NASHORS_TOOTH, LICH_BANE]
    }
    
    # Test scenario: Extended combo vs Bruiser
    level = 13
    combo = ['A', 'Q', 'A', 'E', 'A', 'Q', 'A']  # Longer fight scenario
    target_hp, target_armor, target_mr = 3200, 120, 60  # Typical bruiser stats
    
    print_scenario("2-ITEM BUILDS vs BRUISER", level, combo, target_hp, target_armor, target_mr)
    
    results = {}
    for build_name, items in builds.items():
        result = gwen.calculate_combo_damage(
            combo=combo,
            level=level,
            items=items,
            target_armor=target_armor,
            target_mr=target_mr,
            target_health=target_hp
        )
        results[build_name] = result
        print_build_results(build_name, items, result)
    
    # Compare builds
    sustain_dmg = results["Sustain Build"]["total_dealt"]
    burst_dmg = results["Burst Build"]["total_dealt"]
    dmg_diff = burst_dmg - sustain_dmg
    
    sustain_heal = results["Sustain Build"]["special_effects"]["total_healing"]
    burst_heal = results["Burst Build"]["special_effects"]["total_healing"]
    heal_diff = sustain_heal - burst_heal
    
    print(f"\n📊 COMPARISON:")
    print(f"  Damage: {'Burst' if dmg_diff > 0 else 'Sustain'} Build +{abs(dmg_diff):.0f} damage ({abs(dmg_diff)/min(sustain_dmg, burst_dmg)*100:.1f}% more)")
    print(f"  Healing: Sustain Build +{heal_diff:.0f} healing ({heal_diff/burst_heal*100:.1f}% more)")

def test_2_item_builds_vs_tank():
    """Test 2-item builds against tank target."""
    analyzer = ChampionAnalyzer()
    gwen = analyzer.get_champion("Gwen")
    
    builds = {
        "Sustain Build": [NASHORS_TOOTH, RIFTMAKER],
        "Burst Build": [NASHORS_TOOTH, LICH_BANE]
    }
    
    # Test scenario: All-in combo vs Tank
    level = 13
    combo = ['A', 'Q', 'A', 'E', 'A', 'R', 'A', 'Q', 'A']  # Full all-in with ultimate
    target_hp, target_armor, target_mr = 4500, 180, 90  # Typical tank stats
    
    print_scenario("2-ITEM BUILDS vs TANK", level, combo, target_hp, target_armor, target_mr)
    
    results = {}
    for build_name, items in builds.items():
        result = gwen.calculate_combo_damage(
            combo=combo,
            level=level,
            items=items,
            target_armor=target_armor,
            target_mr=target_mr,
            target_health=target_hp
        )
        results[build_name] = result
        print_build_results(build_name, items, result)
    
    # Compare builds with focus on % HP damage
    sustain_dmg = results["Sustain Build"]["total_dealt"]
    burst_dmg = results["Burst Build"]["total_dealt"]
    dmg_diff = burst_dmg - sustain_dmg
    
    sustain_heal = results["Sustain Build"]["special_effects"]["total_healing"]
    burst_heal = results["Burst Build"]["special_effects"]["total_healing"]
    heal_diff = sustain_heal - burst_heal
    
    # Calculate % HP damage
    sustain_percent = (sustain_dmg / target_hp) * 100
    burst_percent = (burst_dmg / target_hp) * 100
    
    print(f"\n📊 COMPARISON:")
    print(f"  Damage: {'Burst' if dmg_diff > 0 else 'Sustain'} Build +{abs(dmg_diff):.0f} damage ({abs(dmg_diff)/min(sustain_dmg, burst_dmg)*100:.1f}% more)")
    print(f"  Healing: Sustain Build +{heal_diff:.0f} healing ({heal_diff/burst_heal*100:.1f}% more)")
    print(f"  % HP Damage: Sustain {sustain_percent:.1f}% vs Burst {burst_percent:.1f}%")

def test_3_item_builds():
    """Test 3-item builds with Zhonya's addition."""
    analyzer = ChampionAnalyzer()
    gwen = analyzer.get_champion("Gwen")
    
    builds = {
        "Sustain Build": [NASHORS_TOOTH, RIFTMAKER, ZHONYAS_HOURGLASS],
        "Burst Build": [NASHORS_TOOTH, LICH_BANE, ZHONYAS_HOURGLASS]
    }
    
    # Test scenario: Late game teamfight combo
    level = 16
    combo = ['A', 'Q', 'A', 'E', 'A', 'R', 'R', 'R', 'A', 'Q', 'A']  # Full combo with 3 R needles
    target_hp, target_armor, target_mr = 3500, 130, 75  # Mixed resistances target
    
    print_scenario("3-ITEM BUILDS - LATE GAME TEAMFIGHT", level, combo, target_hp, target_armor, target_mr)
    
    results = {}
    for build_name, items in builds.items():
        result = gwen.calculate_combo_damage(
            combo=combo,
            level=level,
            items=items,
            target_armor=target_armor,
            target_mr=target_mr,
            target_health=target_hp
        )
        results[build_name] = result
        print_build_results(build_name, items, result)
    
    # Comprehensive comparison
    sustain_dmg = results["Sustain Build"]["total_dealt"]
    burst_dmg = results["Burst Build"]["total_dealt"]
    dmg_diff = burst_dmg - sustain_dmg
    
    sustain_heal = results["Sustain Build"]["special_effects"]["total_healing"]
    burst_heal = results["Burst Build"]["special_effects"]["total_healing"]
    heal_diff = sustain_heal - burst_heal
    
    # Gold efficiency
    sustain_cost = sum(item.cost for item in builds["Sustain Build"])
    burst_cost = sum(item.cost for item in builds["Burst Build"])
    
    print(f"\n📊 COMPREHENSIVE 3-ITEM COMPARISON:")
    print(f"  Damage: {'Burst' if dmg_diff > 0 else 'Sustain'} Build +{abs(dmg_diff):.0f} damage ({abs(dmg_diff)/min(sustain_dmg, burst_dmg)*100:.1f}% more)")
    print(f"  Healing: Sustain Build +{heal_diff:.0f} healing ({heal_diff/burst_heal*100:.1f}% more)")
    print(f"  Cost: Sustain {sustain_cost:,}g vs Burst {burst_cost:,}g")
    print(f"  Damage/Gold: Sustain {sustain_dmg/sustain_cost:.3f} vs Burst {burst_dmg/burst_cost:.3f}")

def test_level_scaling():
    """Test how builds scale with levels."""
    analyzer = ChampionAnalyzer()
    gwen = analyzer.get_champion("Gwen")
    
    builds = {
        "Sustain": [NASHORS_TOOTH, RIFTMAKER],
        "Burst": [NASHORS_TOOTH, LICH_BANE]
    }
    
    combo = ['A', 'Q', 'A', 'E', 'A']
    target_hp, target_armor, target_mr = 2800, 90, 55  # Balanced target
    
    print_scenario("LEVEL SCALING ANALYSIS", "6-18", combo, target_hp, target_armor, target_mr)
    
    levels = [6, 9, 11, 13, 16, 18]
    
    for level in levels:
        print(f"\n--- Level {level} ---")
        
        for build_name, items in builds.items():
            result = gwen.calculate_combo_damage(
                combo=combo,
                level=level,
                items=items,
                target_armor=target_armor,
                target_mr=target_mr,
                target_health=target_hp
            )
            
            damage = result["total_dealt"]
            healing = result["special_effects"]["total_healing"]
            print(f"  {build_name:7}: {damage:6.0f} dmg | {healing:5.0f} heal")

def test_healing_mechanics():
    """Detailed test of healing mechanics."""
    analyzer = ChampionAnalyzer()
    gwen = analyzer.get_champion("Gwen")
    
    builds = {
        "Riftmaker Only": [RIFTMAKER],
        "Nashor's Only": [NASHORS_TOOTH],
        "Nashor's + Riftmaker": [NASHORS_TOOTH, RIFTMAKER]
    }
    
    combo = ['A', 'Q', 'A', 'E', 'A']
    level = 13
    target_hp, target_armor, target_mr = 3000, 100, 60
    
    print_scenario("HEALING MECHANICS TEST", level, combo, target_hp, target_armor, target_mr)
    
    for build_name, items in builds.items():
        result = gwen.calculate_combo_damage(
            combo=combo,
            level=level,
            items=items,
            target_armor=target_armor,
            target_mr=target_mr,
            target_health=target_hp
        )
        
        special = result["special_effects"]
        print(f"\n{build_name}:")
        print(f"  Total Damage: {result['total_dealt']:.0f}")
        print(f"  Thousand Cuts Healing: {special.get('thousand_cuts_healing', 0):.1f}")
        print(f"  Omnivamp Healing: {special.get('omnivamp_healing', 0):.1f}")
        print(f"  Total Healing: {special.get('total_healing', 0):.1f}")
        print(f"  Heal/Damage Ratio: {special.get('total_healing', 0)/result['total_dealt']:.3f}")

def main():
    """Run all comprehensive tests."""
    print("COMPREHENSIVE GWEN BUILD TESTING")
    print("=" * 80)
    
    try:
        test_basic_functionality()
        test_2_item_builds_vs_squishy()
        test_2_item_builds_vs_bruiser() 
        test_2_item_builds_vs_tank()
        test_3_item_builds()
        test_level_scaling()
        test_healing_mechanics()
        
        print(f"\n{'='*80}")
        print("ALL TESTS COMPLETED SUCCESSFULLY ✓")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()