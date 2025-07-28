#!/usr/bin/env python3
"""
Enhanced mechanics demonstration script.

This script showcases the special mechanics implementation including:
- Eclipse passive (% max HP damage)
- Muramana Shock (mana-based ability damage)
- Smolder Dragon Practice (stacking system)
- Jayce E enhancement (accelerated Q)
- Shyvana E on-hit (% max HP damage)
"""

import matplotlib.pyplot as plt
from pathlib import Path

from lol_analytics.core import ChampionAnalyzer
from lol_analytics.models.item import ECLIPSE, MURAMANA, SERYLDA_GRUDGE, LORD_DOMINIKS, TRINITY_FORCE
from lol_analytics.utils.logger import logger


def demonstrate_eclipse_mechanics():
    """Show Eclipse passive damage scaling."""
    print("\\n" + "="*60)
    print("ECLIPSE PASSIVE DEMONSTRATION")
    print("="*60)
    
    analyzer = ChampionAnalyzer()
    
    # Compare Eclipse vs other items
    builds = {
        "Eclipse + Muramana": [ECLIPSE, MURAMANA],
        "Serylda + Muramana": [SERYLDA_GRUDGE, MURAMANA]
    }
    
    # Test against different HP targets
    hp_targets = [2000, 3000, 4000, 5000]
    
    for target_hp in hp_targets:
        print(f"\\nTarget HP: {target_hp}")
        
        analysis = analyzer.analyze_item_builds(
            champion_name="Jayce",
            combo=['Q2', 'W2'],  # 2 abilities = 1 Eclipse proc
            builds=builds,
            level=13,
            target_stats={"armor": 100, "mr": 70, "health": target_hp}
        )
        
        for build_name, result in analysis['builds'].items():
            damage = result['damage']
            special = damage.get('special_effects', {})
            eclipse_procs = special.get('eclipse_procs', 0)
            
            print(f"  {build_name}: {damage['total_dealt']:.1f} damage (Eclipse procs: {eclipse_procs})")


def demonstrate_muramana_mechanics():
    """Show Muramana scaling with mana and melee vs ranged abilities."""
    print("\\n" + "="*60)
    print("MURAMANA MECHANICS DEMONSTRATION")
    print("="*60)
    
    analyzer = ChampionAnalyzer()
    
    # Test melee vs ranged abilities
    combos = {
        "Jayce Ranged (3%)": ['Q1'],  # Ranged ability - 3% max mana damage
        "Jayce Melee (4%)": ['Q2']    # Melee ability - 4% max mana damage
    }
    
    builds = {"Muramana Only": [MURAMANA]}
    
    for combo_name, combo in combos.items():
        analysis = analyzer.analyze_item_builds(
            champion_name="Jayce",
            combo=combo,
            builds=builds,
            level=13
        )
        
        result = analysis['builds']['Muramana Only']
        damage = result['damage']
        special = damage.get('special_effects', {})
        muramana_ad = special.get('muramana_bonus_ad', 0)
        
        print(f"\\n{combo_name}:")
        print(f"  Total Damage: {damage['total_dealt']:.1f}")
        print(f"  Muramana Bonus AD: {muramana_ad:.1f}")
        print(f"  Raw Physical: {damage['raw_physical']:.1f}")


def demonstrate_smolder_stacking():
    """Show Smolder Dragon Practice stacking effects."""
    print("\\n" + "="*60)
    print("SMOLDER DRAGON PRACTICE STACKING")
    print("="*60)
    
    analyzer = ChampionAnalyzer()
    
    # Test different stack levels
    stack_levels = [0, 50, 100, 150, 200]
    combo = ['Q', 'W', 'E']
    builds = {"Basic Build": []}
    
    for stacks in stack_levels:
        # Create Smolder with specific stack count
        smolder = analyzer.get_champion("Smolder")
        smolder.dragon_practice_stacks = stacks
        
        analysis = analyzer.analyze_item_builds(
            champion_name="Smolder",
            combo=combo,
            builds=builds,
            level=14
        )
        
        result = analysis['builds']['Basic Build']
        damage = result['damage']
        special = damage.get('special_effects', {})
        
        print(f"\\nStacks: {stacks}")
        print(f"  Total Damage: {damage['total_dealt']:.1f}")
        print(f"  Raw Magic: {damage['raw_magic']:.1f}")


def demonstrate_jayce_enhancement():
    """Show Jayce E enhancement mechanics."""
    print("\\n" + "="*60)
    print("JAYCE ENHANCEMENT MECHANICS")
    print("="*60)
    
    analyzer = ChampionAnalyzer()
    
    # Compare regular Q vs enhanced Q
    combos = {
        "Regular Cannon Q": ['Q1'],
        "Enhanced Cannon Q (E1Q1)": ['E1Q1']  # Pre-calculated enhanced version
    }
    
    builds = {"AD Build": [ECLIPSE, MURAMANA]}
    
    for combo_name, combo in combos.items():
        analysis = analyzer.analyze_item_builds(
            champion_name="Jayce",
            combo=combo,
            builds=builds,
            level=13
        )
        
        result = analysis['builds']['AD Build']
        damage = result['damage']
        
        print(f"\\n{combo_name}:")
        print(f"  Total Damage: {damage['total_dealt']:.1f}")
        print(f"  Raw Physical: {damage['raw_physical']:.1f}")


def demonstrate_shyvana_on_hit():
    """Show Shyvana E on-hit % max HP damage."""
    print("\\n" + "="*60)
    print("SHYVANA E ON-HIT MECHANICS")
    print("="*60)
    
    analyzer = ChampionAnalyzer()
    
    # Test against different HP targets
    hp_targets = [2000, 3000, 4000, 5000]
    combo = ['E']  # Flame Breath with 3% max HP on-hit
    builds = {"AP Build": []}
    
    for target_hp in hp_targets:
        analysis = analyzer.analyze_item_builds(
            champion_name="Shyvana",
            combo=combo,
            builds=builds,
            level=13,
            target_stats={"armor": 100, "mr": 70, "health": target_hp}
        )
        
        result = analysis['builds']['AP Build']
        damage = result['damage']
        
        print(f"\\nTarget HP: {target_hp}")
        print(f"  Total Damage: {damage['total_dealt']:.1f}")
        print(f"  Raw Magic: {damage['raw_magic']:.1f}")


def comprehensive_build_comparison():
    """Compare builds with all special mechanics active."""
    print("\\n" + "="*60)
    print("COMPREHENSIVE BUILD COMPARISON")
    print("="*60)
    
    analyzer = ChampionAnalyzer()
    
    # Jayce full combo with all mechanics
    builds = {
        "Eclipse + Muramana + Serylda": [ECLIPSE, MURAMANA, SERYLDA_GRUDGE],
        "Trinity + Muramana + LDR": [TRINITY_FORCE, MURAMANA, LORD_DOMINIKS]
    }
    
    # Full Jayce combo including enhanced Q
    jayce_combo = ['Q2', 'W2', 'E2', 'E1Q1', 'W1A', 'W1A']  # Multiple Eclipse procs
    
    analysis = analyzer.analyze_item_builds(
        champion_name="Jayce",
        combo=jayce_combo,
        builds=builds,
        level=13,
        target_stats={"armor": 120, "mr": 70, "health": 3000}
    )
    
    print(f"\\nJayce Full Combo Analysis:")
    print(f"Best Build: {analysis['best_build']}")
    
    for build_name, result in analysis['builds'].items():
        damage = result['damage']
        special = damage.get('special_effects', {})
        
        print(f"\\n{build_name}:")
        print(f"  Total Damage: {damage['total_dealt']:.1f}")
        print(f"  Physical: {damage['physical_dealt']:.1f}")
        print(f"  Magic: {damage['magic_dealt']:.1f}")
        print(f"  Eclipse Procs: {special.get('eclipse_procs', 0)}")
        print(f"  Muramana Bonus AD: {special.get('muramana_bonus_ad', 0):.1f}")
        print(f"  Effective Armor: {special.get('effective_armor', 0):.1f}")
        print(f"  Cost: {result['total_cost']} gold")
        print(f"  Damage/Gold: {result['damage_per_gold']:.3f}")


def main():
    """Run all special mechanics demonstrations."""
    logger.info("Starting Enhanced Mechanics Demonstration")
    
    try:
        demonstrate_eclipse_mechanics()
        demonstrate_muramana_mechanics()
        demonstrate_smolder_stacking()
        demonstrate_jayce_enhancement()
        demonstrate_shyvana_on_hit()
        comprehensive_build_comparison()
        
        print("\\n" + "="*60)
        print("SPECIAL MECHANICS DEMONSTRATION COMPLETE")
        print("="*60)
        print("\\nKey Features Demonstrated:")
        print("✅ Eclipse: % max HP damage every 2 ability hits")
        print("✅ Muramana: Mana-based ability damage (4% melee, 3% ranged)")
        print("✅ Smolder: Dragon Practice stacking system")
        print("✅ Jayce: E enhancement for Q abilities")
        print("✅ Shyvana: E on-hit % max HP damage")
        print("✅ Accurate armor penetration calculations")
        print("✅ Item passive interactions")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    main()