#!/usr/bin/env python3
"""
Example script demonstrating the modernized League of Legends analytics system.

This script shows how to use the new object-oriented, type-safe architecture
for champion damage analysis and professional player tracking.
"""

import matplotlib.pyplot as plt
from pathlib import Path

# Import the modernized analytics system
from lol_analytics.core import ChampionAnalyzer, PlayerTracker
from lol_analytics.models.item import ITEM_SETS, ECLIPSE, MURAMANA, SERYLDA_GRUDGE, LORD_DOMINIKS
from lol_analytics.utils.logger import logger


def main():
    """Run example analyses."""
    
    logger.info("Starting League of Legends Analytics Example")
    
    # Initialize analyzers
    analyzer = ChampionAnalyzer()
    tracker = PlayerTracker()
    
    # Example 1: Jayce Build Comparison (modernized version of your original analysis)
    print("\\n" + "="*60)
    print("EXAMPLE 1: Jayce Build Comparison")
    print("="*60)
    
    # Define the builds we want to compare
    builds = {
        "Eclipse + Muramana + Serylda": [ECLIPSE, MURAMANA, SERYLDA_GRUDGE],
        "Eclipse + Muramana + LDR": [ECLIPSE, MURAMANA, LORD_DOMINIKS]
    }
    
    # Define the combo (from your original analysis)
    jayce_combo = ['Q2', 'W2', 'E2', 'R1', 'E1Q1', 'W1A', 'W1A', 'W1A']
    
    # Run the analysis
    try:
        analysis = analyzer.analyze_item_builds(
            champion_name="Jayce",
            combo=jayce_combo,
            builds=builds,
            level=13,
            target_stats={"armor": 100, "mr": 70, "health": 3000}
        )
        
        print(f"\\nBest Build: {analysis['best_build']}")
        print(f"Highest Damage: {analysis['analysis_summary']['highest_damage']:.1f}")
        print(f"Most Efficient: {analysis['analysis_summary']['most_efficient']}")
        
        # Print detailed results
        for build_name, result in analysis['builds'].items():
            damage = result['damage']
            print(f"\\n{build_name}:")
            print(f"  Total Damage: {damage['total_dealt']:.1f}")
            print(f"  Physical: {damage['physical_dealt']:.1f}")
            print(f"  Magic: {damage['magic_dealt']:.1f}")
            print(f"  Cost: {result['total_cost']} gold")
            print(f"  Damage/Gold: {result['damage_per_gold']:.3f}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
    
    # Example 2: Armor Range Analysis (enhanced version)
    print("\\n" + "="*60)
    print("EXAMPLE 2: Damage vs Armor Analysis")
    print("="*60)
    
    try:
        armor_analysis = analyzer.run_armor_analysis(
            champion_name="Jayce",
            combo=jayce_combo,
            builds=builds,
            level=13,
            armor_range=(30, 200),
            save_plot=True
        )
        
        print(f"\\nArmor analysis complete for {armor_analysis['champion']}")
        print(f"Builds compared: {', '.join(armor_analysis['builds'])}")
        
        if armor_analysis['crossover_analysis']:
            print("\\nCrossover points found:")
            for comparison, points in armor_analysis['crossover_analysis'].items():
                print(f"  {comparison}: {[f'{p:.1f}' for p in points]}")
        
    except Exception as e:
        logger.error(f"Armor analysis failed: {e}")
    
    # Example 3: Smolder Analysis (fixed implementation)
    print("\\n" + "="*60)
    print("EXAMPLE 3: Smolder Build Analysis")
    print("="*60)
    
    smolder_builds = {
        "ER + Trinity + Muramana": ITEM_SETS["ER_Trinity_Muramana"],
        "ER + Trinity + Shojin": ITEM_SETS["ER_Trinity_Shojin"]
    }
    
    smolder_combo = ['R', 'W', 'A', 'Q']
    
    try:
        smolder_analysis = analyzer.analyze_item_builds(
            champion_name="Smolder",
            combo=smolder_combo,
            builds=smolder_builds,
            level=14
        )
        
        print(f"\\nSmolder Analysis Complete")
        print(f"Best Build: {smolder_analysis['best_build']}")
        
        for build_name, result in smolder_analysis['builds'].items():
            damage = result['damage']
            print(f"\\n{build_name}: {damage['total_dealt']:.1f} damage")
        
    except Exception as e:
        logger.error(f"Smolder analysis failed: {e}")
    
    # Example 4: Champion Comparison
    print("\\n" + "="*60)
    print("EXAMPLE 4: Multi-Champion Comparison")
    print("="*60)
    
    try:
        # Compare all champions with same build and combo
        comparison = analyzer.compare_champions(
            champion_names=["Jayce", "Smolder", "Shyvana"],
            combo=['Q', 'A'],  # Simple combo all can use
            items=[ECLIPSE, MURAMANA],
            level=13
        )
        
        print("\\nChampion Ranking (by damage):")
        for i, champ in enumerate(comparison['ranking'], 1):
            damage = comparison['results'][champ]['total_dealt']
            print(f"{i}. {champ}: {damage:.1f} damage")
        
        if comparison['damage_differences']:
            print("\\nDamage differences from top:")
            for champ, diff in comparison['damage_differences'].items():
                print(f"  {champ}: -{diff:.1f} damage")
        
    except Exception as e:
        logger.error(f"Champion comparison failed: {e}")
    
    # Example 5: Professional Player Tracking (requires API key)
    print("\\n" + "="*60)
    print("EXAMPLE 5: Professional Player Tracking")
    print("="*60)
    
    # Note: This requires a valid API key in .env file
    try:
        # Add a few test players
        test_players = [
            {"game_name": "RoseThorn", "tag_line": "Rose", "team": "TEST", "role": "BOTTOM"}
        ]
        
        results = tracker.batch_add_players(test_players)
        
        for display_name, player in results.items():
            if player:
                print(f"Added: {player.display_name} ({player.team} - {player.role})")
            else:
                print(f"Failed to add: {display_name}")
        
        # Save the data
        tracker.save_player_data("example_players.json")
        
    except Exception as e:
        logger.warning(f"Player tracking example skipped (likely missing API key): {e}")
    
    print("\\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("\\nCheck the 'data' directory for:")
    print("- Saved plots (PNG files)")
    print("- Analysis results (JSON files)")
    print("- Player data (JSON files)")
    print("\\nLogs are saved to 'logs/analytics.log'")


if __name__ == "__main__":
    main()