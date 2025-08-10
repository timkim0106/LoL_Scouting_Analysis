#!/usr/bin/env python3
"""
Comprehensive Gwen Build Analysis Script

Compares Riftmaker vs Glass Cannon builds:
- Nashor's Tooth + Riftmaker vs Nashor's Tooth + Lich Bane
- 2-item and 3-item (+ Zhonya's) comparisons
- Damage and healing calculations across varying enemy stats and Gwen levels
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple

from lol_analytics.core import ChampionAnalyzer
from lol_analytics.models.item import (
    NASHORS_TOOTH, RIFTMAKER, LICH_BANE, ZHONYAS_HOURGLASS,
    ITEM_SETS
)
from lol_analytics.utils.logger import logger

# Set up plotting style
try:
    import seaborn as sns
    plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
    sns.set_palette("husl")
except ImportError:
    plt.style.use('default')


def analyze_gwen_builds():
    """Main analysis function for Gwen builds."""
    print("\n" + "="*70)
    print("GWEN BUILD ANALYSIS: RIFTMAKER VS GLASS CANNON")
    print("="*70)
    
    analyzer = ChampionAnalyzer()
    gwen = analyzer.get_champion("Gwen")
    
    # Build configurations
    builds_2_item = {
        "Nashor's + Riftmaker": ITEM_SETS["Nashors_Riftmaker"],
        "Nashor's + Lich Bane": ITEM_SETS["Nashors_LichBane"]
    }
    
    builds_3_item = {
        "Nashor's + Riftmaker + Zhonya's": ITEM_SETS["Nashors_Riftmaker_Zhonyas"],
        "Nashor's + Lich Bane + Zhonya's": ITEM_SETS["Nashors_LichBane_Zhonyas"]
    }
    
    # Standard combo: Auto + Q + Auto + E (enhanced) + Auto
    standard_combo = ['A', 'Q', 'A', 'E', 'A']
    
    # Extended combo with R: Auto + Q + Auto + E + Auto + R (3 needles)
    extended_combo = ['A', 'Q', 'A', 'E', 'A', 'R', 'R', 'R']
    
    print("\n2-ITEM BUILD COMPARISON")
    print("-" * 40)
    
    # Analysis across different scenarios
    analyze_level_scaling(analyzer, builds_2_item, standard_combo, "2-Item")
    analyze_enemy_tankiness(analyzer, builds_2_item, standard_combo, "2-Item")
    analyze_healing_efficiency(analyzer, builds_2_item, standard_combo, "2-Item")
    
    print("\n3-ITEM BUILD COMPARISON")
    print("-" * 40)
    
    analyze_level_scaling(analyzer, builds_3_item, extended_combo, "3-Item")
    analyze_enemy_tankiness(analyzer, builds_3_item, extended_combo, "3-Item")
    analyze_healing_efficiency(analyzer, builds_3_item, extended_combo, "3-Item")
    
    # Gold efficiency analysis
    analyze_gold_efficiency(builds_2_item, builds_3_item)
    
    # Create comprehensive comparison plots
    create_damage_comparison_plots(analyzer, builds_2_item, builds_3_item)
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE - Check 'data/' directory for plots")
    print("="*70)


def analyze_level_scaling(analyzer, builds: Dict[str, List], combo: List[str], build_type: str):
    """Analyze how builds scale across Gwen levels."""
    print(f"\n{build_type} Level Scaling Analysis:")
    print("-" * 30)
    
    levels = [6, 9, 11, 13, 16, 18]
    target_stats = {"armor": 80, "mr": 50, "health": 2500}
    
    results = {}
    for level in levels:
        level_results = {}
        for build_name, items in builds.items():
            analysis = analyzer.analyze_item_builds(
                champion_name="Gwen",
                combo=combo,
                builds={build_name: items},
                level=level,
                target_stats=target_stats
            )
            
            damage_result = analysis['builds'][build_name]['damage']
            level_results[build_name] = {
                'total_damage': damage_result['total_dealt'],
                'thousand_cuts_damage': damage_result['special_effects']['thousand_cuts_damage'],
                'thousand_cuts_healing': damage_result['special_effects']['thousand_cuts_healing']
            }
        
        results[level] = level_results
        
        # Print level comparison
        riftmaker_build = next(k for k in level_results.keys() if 'Riftmaker' in k)
        lichbane_build = next(k for k in level_results.keys() if 'Lich Bane' in k)
        
        riftmaker_dmg = level_results[riftmaker_build]['total_damage']
        lichbane_dmg = level_results[lichbane_build]['total_damage']
        damage_diff = riftmaker_dmg - lichbane_dmg
        
        print(f"Level {level:2d}: Riftmaker {riftmaker_dmg:6.1f} vs Lich Bane {lichbane_dmg:6.1f} "
              f"({'+'if damage_diff > 0 else ''}{damage_diff:5.1f} damage)")


def analyze_enemy_tankiness(analyzer, builds: Dict[str, List], combo: List[str], build_type: str):
    """Analyze builds against different enemy tankiness levels."""
    print(f"\n{build_type} Enemy Tankiness Analysis:")
    print("-" * 35)
    
    # Different enemy profiles
    enemy_profiles = {
        "Squishy ADC": {"armor": 65, "mr": 35, "health": 2200},
        "Bruiser": {"armor": 120, "mr": 60, "health": 3200},
        "Tank": {"armor": 180, "mr": 90, "health": 4500}
    }
    
    level = 13  # Mid-game level
    
    for enemy_type, target_stats in enemy_profiles.items():
        print(f"\nVs {enemy_type} ({target_stats['armor']} Armor, {target_stats['mr']} MR, {target_stats['health']} HP):")
        
        best_damage = 0
        best_build = ""
        
        for build_name, items in builds.items():
            analysis = analyzer.analyze_item_builds(
                champion_name="Gwen",
                combo=combo,
                builds={build_name: items},
                level=level,
                target_stats=target_stats
            )
            
            damage_result = analysis['builds'][build_name]['damage']
            total_damage = damage_result['total_dealt']
            thousand_cuts = damage_result['special_effects']['thousand_cuts_damage']
            
            if total_damage > best_damage:
                best_damage = total_damage
                best_build = build_name
            
            print(f"  {build_name}: {total_damage:.1f} total ({thousand_cuts:.1f} Thousand Cuts)")
        
        print(f"  → Best: {best_build}")


def analyze_healing_efficiency(analyzer, builds: Dict[str, List], combo: List[str], build_type: str):
    """Analyze healing efficiency of different builds."""
    print(f"\n{build_type} Healing Efficiency:")
    print("-" * 28)
    
    level = 13
    target_stats = {"armor": 100, "mr": 60, "health": 3000}
    
    for build_name, items in builds.items():
        analysis = analyzer.analyze_item_builds(
            champion_name="Gwen",
            combo=combo,
            builds={build_name: items},
            level=level,
            target_stats=target_stats
        )
        
        damage_result = analysis['builds'][build_name]['damage']
        healing = damage_result['special_effects']['thousand_cuts_healing']
        total_damage = damage_result['total_dealt']
        
        # Calculate healing per damage point
        healing_efficiency = healing / total_damage if total_damage > 0 else 0
        
        # Get omnivamp healing from special effects
        omnivamp_healing = damage_result['special_effects'].get('omnivamp_healing', 0)
        total_healing_from_result = damage_result['special_effects'].get('total_healing', healing)
        
        print(f"  {build_name}:")
        print(f"    Thousand Cuts healing: {healing:.1f}")
        print(f"    Omnivamp healing: {omnivamp_healing:.1f}")
        print(f"    Total healing: {total_healing_from_result:.1f}")
        print(f"    Healing/Damage ratio: {total_healing_from_result/total_damage:.3f}")


def analyze_gold_efficiency(builds_2_item: Dict, builds_3_item: Dict):
    """Analyze gold efficiency of different builds."""
    print(f"\nGold Efficiency Analysis:")
    print("-" * 26)
    
    def calculate_build_cost(items):
        return sum(item.cost for item in items)
    
    def calculate_stats_value(items):
        total_ap = sum(item.effects.ability_power for item in items)
        total_cdr = sum(item.effects.ability_haste for item in items)
        total_as = sum(item.effects.attack_speed for item in items)
        total_hp = sum(item.effects.health for item in items)
        total_armor = sum(item.effects.armor for item in items)
        
        # Approximate gold values (standard LoL values)
        ap_value = total_ap * 21.75  # 21.75g per AP
        cdr_value = total_cdr * 26.67  # ~26.67g per AH
        as_value = total_as * 2500  # ~25g per 1% AS
        hp_value = total_hp * 2.67  # 2.67g per HP
        armor_value = total_armor * 20  # 20g per armor
        
        return ap_value + cdr_value + as_value + hp_value + armor_value
    
    all_builds = {**builds_2_item, **builds_3_item}
    
    for build_name, items in all_builds.items():
        cost = calculate_build_cost(items)
        stats_value = calculate_stats_value(items)
        efficiency = (stats_value / cost) * 100 if cost > 0 else 0
        
        print(f"  {build_name}:")
        print(f"    Total cost: {cost:,}g")
        print(f"    Stats value: {stats_value:.0f}g")
        print(f"    Efficiency: {efficiency:.1f}%")


def create_damage_comparison_plots(analyzer, builds_2_item: Dict, builds_3_item: Dict):
    """Create comprehensive damage comparison plots."""
    combo = ['A', 'Q', 'A', 'E', 'A']
    
    # Create armor vs damage plots
    create_armor_damage_plots(analyzer, builds_2_item, builds_3_item, combo)
    
    # Create level scaling plots  
    create_level_scaling_plots(analyzer, builds_2_item, builds_3_item, combo)
    
    # Create healing comparison plots
    create_healing_comparison_plots(analyzer, builds_2_item, builds_3_item, combo)


def create_armor_damage_plots(analyzer, builds_2_item: Dict, builds_3_item: Dict, combo: List[str]):
    """Create armor vs damage plots."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    armor_range = np.linspace(50, 200, 50)
    level = 13
    target_hp = 3000
    target_mr = 60
    
    # 2-item builds
    for build_name, items in builds_2_item.items():
        damages = []
        for armor in armor_range:
            result = analyzer.get_champion("Gwen").calculate_combo_damage(
                combo=combo,
                level=level,
                items=items,
                target_armor=armor,
                target_mr=target_mr,
                target_health=target_hp
            )
            damages.append(result['total_dealt'])
        
        ax1.plot(armor_range, damages, label=build_name, linewidth=2)
    
    ax1.set_title('2-Item Builds: Damage vs Armor')
    ax1.set_xlabel('Enemy Armor')
    ax1.set_ylabel('Total Damage')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 3-item builds
    extended_combo = combo + ['R', 'R', 'R']
    for build_name, items in builds_3_item.items():
        damages = []
        for armor in armor_range:
            result = analyzer.get_champion("Gwen").calculate_combo_damage(
                combo=extended_combo,
                level=level,
                items=items,
                target_armor=armor,
                target_mr=target_mr,
                target_health=target_hp
            )
            damages.append(result['total_dealt'])
        
        ax2.plot(armor_range, damages, label=build_name, linewidth=2)
    
    ax2.set_title('3-Item Builds: Damage vs Armor')
    ax2.set_xlabel('Enemy Armor')
    ax2.set_ylabel('Total Damage')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Damage differential plots
    riftmaker_2_damages = []
    lichbane_2_damages = []
    
    for armor in armor_range:
        rf_result = analyzer.get_champion("Gwen").calculate_combo_damage(
            combo=combo, level=level, items=builds_2_item["Nashor's + Riftmaker"],
            target_armor=armor, target_mr=target_mr, target_health=target_hp
        )
        lb_result = analyzer.get_champion("Gwen").calculate_combo_damage(
            combo=combo, level=level, items=builds_2_item["Nashor's + Lich Bane"],
            target_armor=armor, target_mr=target_mr, target_health=target_hp
        )
        
        riftmaker_2_damages.append(rf_result['total_dealt'])
        lichbane_2_damages.append(lb_result['total_dealt'])
    
    differential = np.array(riftmaker_2_damages) - np.array(lichbane_2_damages)
    ax3.plot(armor_range, differential, linewidth=3, color='red')
    ax3.axhline(y=0, color='black', linestyle='--', alpha=0.7)
    ax3.fill_between(armor_range, differential, 0, 
                     where=(differential > 0), alpha=0.3, color='green', label='Riftmaker Advantage')
    ax3.fill_between(armor_range, differential, 0, 
                     where=(differential < 0), alpha=0.3, color='red', label='Lich Bane Advantage')
    
    ax3.set_title('2-Item Damage Differential: Riftmaker - Lich Bane')
    ax3.set_xlabel('Enemy Armor')
    ax3.set_ylabel('Damage Difference')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Health scaling comparison
    health_range = np.linspace(2000, 5000, 50)
    armor = 100
    
    rf_hp_damages = []
    lb_hp_damages = []
    
    for hp in health_range:
        rf_result = analyzer.get_champion("Gwen").calculate_combo_damage(
            combo=combo, level=level, items=builds_2_item["Nashor's + Riftmaker"],
            target_armor=armor, target_mr=target_mr, target_health=hp
        )
        lb_result = analyzer.get_champion("Gwen").calculate_combo_damage(
            combo=combo, level=level, items=builds_2_item["Nashor's + Lich Bane"],
            target_armor=armor, target_mr=target_mr, target_health=hp
        )
        
        rf_hp_damages.append(rf_result['total_dealt'])
        lb_hp_damages.append(lb_result['total_dealt'])
    
    ax4.plot(health_range, rf_hp_damages, label="Nashor's + Riftmaker", linewidth=2)
    ax4.plot(health_range, lb_hp_damages, label="Nashor's + Lich Bane", linewidth=2)
    
    ax4.set_title('2-Item Builds: Damage vs Enemy Health')
    ax4.set_xlabel('Enemy Health')
    ax4.set_ylabel('Total Damage')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/gwen_armor_damage_analysis.png', dpi=300, bbox_inches='tight')
    logger.info("Armor damage analysis plot saved to: data/gwen_armor_damage_analysis.png")


def create_level_scaling_plots(analyzer, builds_2_item: Dict, builds_3_item: Dict, combo: List[str]):
    """Create level scaling plots."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    levels = range(6, 19)
    target_stats = {"armor": 80, "mr": 50, "health": 2500}
    
    # 2-item level scaling
    for build_name, items in builds_2_item.items():
        damages = []
        healings = []
        
        for level in levels:
            result = analyzer.get_champion("Gwen").calculate_combo_damage(
                combo=combo,
                level=level,
                items=items,
                target_armor=target_stats["armor"],
                target_mr=target_stats["mr"],
                target_health=target_stats["health"]
            )
            damages.append(result['total_dealt'])
            healings.append(result['special_effects']['thousand_cuts_healing'])
        
        ax1.plot(levels, damages, label=f"{build_name} (Damage)", linewidth=2, marker='o')
        ax1.plot(levels, healings, label=f"{build_name} (Healing)", linewidth=2, linestyle='--', marker='s')
    
    ax1.set_title('Level Scaling: Damage & Healing (2-Item)')
    ax1.set_xlabel('Champion Level')
    ax1.set_ylabel('Damage / Healing')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 3-item level scaling
    extended_combo = combo + ['R', 'R', 'R']
    for build_name, items in builds_3_item.items():
        damages = []
        healings = []
        
        for level in levels:
            result = analyzer.get_champion("Gwen").calculate_combo_damage(
                combo=extended_combo,
                level=level,
                items=items,
                target_armor=target_stats["armor"],
                target_mr=target_stats["mr"],
                target_health=target_stats["health"]
            )
            damages.append(result['total_dealt'])
            healings.append(result['special_effects']['thousand_cuts_healing'])
        
        ax2.plot(levels, damages, label=f"{build_name} (Damage)", linewidth=2, marker='o')
        ax2.plot(levels, healings, label=f"{build_name} (Healing)", linewidth=2, linestyle='--', marker='s')
    
    ax2.set_title('Level Scaling: Damage & Healing (3-Item)')
    ax2.set_xlabel('Champion Level')
    ax2.set_ylabel('Damage / Healing')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/gwen_level_scaling_analysis.png', dpi=300, bbox_inches='tight')
    logger.info("Level scaling analysis plot saved to: data/gwen_level_scaling_analysis.png")


def create_healing_comparison_plots(analyzer, builds_2_item: Dict, builds_3_item: Dict, combo: List[str]):
    """Create healing comparison plots."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Healing vs different enemy HP pools
    hp_range = np.linspace(2000, 5000, 30)
    level = 13
    armor = 100
    mr = 60
    
    for build_name, items in builds_2_item.items():
        thousand_cuts_healings = []
        total_healings = []
        
        for hp in hp_range:
            result = analyzer.get_champion("Gwen").calculate_combo_damage(
                combo=combo,
                level=level,
                items=items,
                target_armor=armor,
                target_mr=mr,
                target_health=hp
            )
            
            tc_healing = result['special_effects']['thousand_cuts_healing']
            
            # Add omnivamp healing if Riftmaker
            omnivamp_healing = 0
            for item in items:
                if item.effects.omnivamp > 0:
                    omnivamp_healing = result['total_dealt'] * item.effects.omnivamp
            
            thousand_cuts_healings.append(tc_healing)
            total_healings.append(tc_healing + omnivamp_healing)
        
        ax1.plot(hp_range, thousand_cuts_healings, label=f"{build_name} (Thousand Cuts)", linewidth=2)
        ax1.plot(hp_range, total_healings, label=f"{build_name} (Total Healing)", linewidth=2, linestyle='--')
    
    ax1.set_title('Healing vs Enemy Health (2-Item)')
    ax1.set_xlabel('Enemy Health')
    ax1.set_ylabel('Healing Per Combo')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Healing efficiency comparison
    levels = range(6, 19)
    target_stats = {"armor": 100, "mr": 60, "health": 3000}
    
    for build_name, items in builds_2_item.items():
        healing_ratios = []
        
        for level in levels:
            result = analyzer.get_champion("Gwen").calculate_combo_damage(
                combo=combo,
                level=level,
                items=items,
                target_armor=target_stats["armor"],
                target_mr=target_stats["mr"],
                target_health=target_stats["health"]
            )
            
            tc_healing = result['special_effects']['thousand_cuts_healing']
            total_damage = result['total_dealt']
            
            # Add omnivamp healing
            omnivamp_healing = 0
            for item in items:
                if item.effects.omnivamp > 0:
                    omnivamp_healing = total_damage * item.effects.omnivamp
            
            total_healing = tc_healing + omnivamp_healing
            healing_ratio = total_healing / total_damage if total_damage > 0 else 0
            healing_ratios.append(healing_ratio)
        
        ax2.plot(levels, healing_ratios, label=build_name, linewidth=2, marker='o')
    
    ax2.set_title('Healing Efficiency by Level (2-Item)')
    ax2.set_xlabel('Champion Level')
    ax2.set_ylabel('Total Healing / Damage Dealt')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/gwen_healing_analysis.png', dpi=300, bbox_inches='tight')
    logger.info("Healing analysis plot saved to: data/gwen_healing_analysis.png")


if __name__ == "__main__":
    # Create data directory if it doesn't exist
    Path("data").mkdir(exist_ok=True)
    
    # Run the analysis
    analyze_gwen_builds()