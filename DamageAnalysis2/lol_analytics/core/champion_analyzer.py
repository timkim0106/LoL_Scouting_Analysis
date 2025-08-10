"""Core champion analysis functionality."""

from typing import Dict, List, Optional, Tuple, Any
import json
from pathlib import Path

from ..models.champion import Champion, Smolder, Jayce, Shyvana, Gwen
from ..models.item import Item, ITEM_SETS
from ..analytics.damage_calculator import DamageCalculator
from ..utils.logger import logger


class ChampionAnalyzer:
    """
    Main class for analyzing champion damage and performance.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the champion analyzer.
        
        Args:
            data_dir: Directory for storing analysis data
        """
        self.data_dir = data_dir or Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.damage_calculator = DamageCalculator()
        self.champions: Dict[str, Champion] = self._load_champions()
        
        logger.info(f"ChampionAnalyzer initialized with {len(self.champions)} champions")
    
    def _load_champions(self) -> Dict[str, Champion]:
        """Load available champions."""
        champions = {
            "Smolder": Smolder(),
            "Jayce": Jayce(),
            "Shyvana": Shyvana(),
            "Gwen": Gwen()
        }
        return champions
    
    def get_champion(self, name: str) -> Champion:
        """
        Get a champion by name.
        
        Args:
            name: Champion name
        
        Returns:
            Champion instance
        
        Raises:
            ValueError: If champion not found
        """
        if name not in self.champions:
            available = list(self.champions.keys())
            raise ValueError(f"Champion '{name}' not found. Available: {available}")
        
        return self.champions[name]
    
    def analyze_item_builds(
        self,
        champion_name: str,
        combo: List[str],
        builds: Dict[str, List[Item]],
        level: int = 13,
        target_stats: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Analyze different item builds for a champion.
        
        Args:
            champion_name: Name of the champion
            combo: List of ability names for the combo
            builds: Dictionary mapping build names to item lists
            level: Champion level
            target_stats: Target stats (armor, MR, health)
        
        Returns:
            Analysis results
        """
        if target_stats is None:
            target_stats = {"armor": 100, "mr": 70, "health": 3000}
        
        champion = self.get_champion(champion_name)
        
        logger.info(f"Analyzing {len(builds)} builds for {champion_name}")
        
        # Calculate damage for each build
        build_results = {}
        for build_name, items in builds.items():
            damage_result = champion.calculate_combo_damage(
                combo=combo,
                level=level,
                items=items,
                target_armor=target_stats["armor"],
                target_mr=target_stats["mr"],
                target_health=target_stats["health"]
            )
            
            build_results[build_name] = {
                "damage": damage_result,
                "items": [item.name for item in items],
                "total_cost": sum(item.cost for item in items)
            }
        
        # Find best build
        best_build = max(build_results.keys(), 
                        key=lambda b: build_results[b]["damage"]["total_dealt"])
        
        # Calculate gold efficiency
        for build_name, result in build_results.items():
            if result["total_cost"] > 0:
                damage_per_gold = result["damage"]["total_dealt"] / result["total_cost"]
            else:
                damage_per_gold = result["damage"]["total_dealt"]  # No items = damage per 1 gold
            result["damage_per_gold"] = damage_per_gold
        
        analysis = {
            "champion": champion_name,
            "combo": combo,
            "level": level,
            "target_stats": target_stats,
            "builds": build_results,
            "best_build": best_build,
            "analysis_summary": {
                "highest_damage": build_results[best_build]["damage"]["total_dealt"],
                "most_efficient": max(build_results.keys(), 
                                    key=lambda b: build_results[b]["damage_per_gold"])
            }
        }
        
        logger.info(f"Analysis complete. Best build: {best_build}")
        
        return analysis
    
    def compare_champions(
        self,
        champion_names: List[str],
        combo: List[str],
        items: List[Item],
        level: int = 13,
        target_stats: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Compare damage output across multiple champions.
        
        Args:
            champion_names: List of champion names
            combo: Ability combo to test
            items: Item build to use
            level: Champion level
            target_stats: Target stats
        
        Returns:
            Comparison results
        """
        if target_stats is None:
            target_stats = {"armor": 100, "mr": 70, "health": 3000}
        
        results = {}
        
        for champ_name in champion_names:
            try:
                champion = self.get_champion(champ_name)
                damage_result = champion.calculate_combo_damage(
                    combo=combo,
                    level=level,
                    items=items,
                    target_armor=target_stats["armor"],
                    target_mr=target_stats["mr"],
                    target_health=target_stats["health"]
                )
                results[champ_name] = damage_result
            except ValueError as e:
                logger.warning(f"Skipping {champ_name}: {e}")
        
        # Rank by total damage
        ranking = sorted(results.keys(), 
                        key=lambda c: results[c]["total_dealt"], 
                        reverse=True)
        
        comparison = {
            "champions": champion_names,
            "combo": combo,
            "items": [item.name for item in items],
            "level": level,
            "target_stats": target_stats,
            "results": results,
            "ranking": ranking,
            "damage_differences": {}
        }
        
        # Calculate differences from top performer
        if ranking:
            top_damage = results[ranking[0]]["total_dealt"]
            for champ in ranking[1:]:
                diff = top_damage - results[champ]["total_dealt"]
                comparison["damage_differences"][champ] = diff
        
        return comparison
    
    def run_armor_analysis(
        self,
        champion_name: str,
        combo: List[str],
        builds: Dict[str, List[Item]],
        level: int = 13,
        armor_range: Tuple[float, float] = (30, 200),
        save_plot: bool = True
    ) -> Dict[str, Any]:
        """
        Run armor-based damage analysis.
        
        Args:
            champion_name: Champion name
            combo: Ability combo
            builds: Item builds to compare
            level: Champion level
            armor_range: Range of armor values to test
            save_plot: Whether to save the plot
        
        Returns:
            Analysis results with plot data
        """
        champion = self.get_champion(champion_name)
        
        # Calculate damage across armor range for each build
        comparison_data = self.damage_calculator.compare_item_builds(
            champion=champion,
            combo=combo,
            item_builds=builds,
            level=level,
            armor_range=armor_range
        )
        
        # Create plot
        plot_title = f"{champion_name} Level {level} - Damage vs Armor"
        fig = self.damage_calculator.plot_damage_comparison(
            comparison_data=comparison_data,
            title=plot_title
        )
        
        if save_plot:
            plot_path = self.data_dir / f"{champion_name}_armor_analysis_{level}.png"
            fig.savefig(plot_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to: {plot_path}")
        
        # Find crossover points
        crossover_analysis = self._analyze_crossovers(comparison_data)
        
        results = {
            "champion": champion_name,
            "combo": combo,
            "level": level,
            "armor_range": armor_range,
            "builds": list(builds.keys()),
            "comparison_data": comparison_data,
            "crossover_analysis": crossover_analysis,
            "plot_saved": save_plot
        }
        
        return results
    
    def _analyze_crossovers(self, comparison_data: Dict[str, Tuple]) -> Dict[str, Any]:
        """Analyze crossover points between different builds."""
        build_names = list(comparison_data.keys())
        crossovers = {}
        
        if len(build_names) >= 2:
            for i in range(len(build_names)):
                for j in range(i + 1, len(build_names)):
                    build1, build2 = build_names[i], build_names[j]
                    armor_vals, damage1 = comparison_data[build1]
                    _, damage2 = comparison_data[build2]
                    
                    # Find where lines cross
                    diff = damage1 - damage2
                    sign_changes = []
                    
                    for k in range(len(diff) - 1):
                        if (diff[k] > 0) != (diff[k + 1] > 0):
                            # Linear interpolation to find exact crossover
                            x1, x2 = armor_vals[k], armor_vals[k + 1]
                            y1, y2 = diff[k], diff[k + 1]
                            crossover = x1 - y1 * (x2 - x1) / (y2 - y1)
                            sign_changes.append(crossover)
                    
                    if sign_changes:
                        crossovers[f"{build1}_vs_{build2}"] = sign_changes
        
        return crossovers
    
    def save_analysis(self, analysis: Dict[str, Any], filename: str) -> Path:
        """
        Save analysis results to JSON file.
        
        Args:
            analysis: Analysis results
            filename: Output filename
        
        Returns:
            Path to saved file
        """
        output_path = self.data_dir / filename
        
        # Convert numpy arrays to lists for JSON serialization
        def convert_numpy(obj):
            if hasattr(obj, 'tolist'):
                return obj.tolist()
            return obj
        
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2, default=convert_numpy)
        
        logger.info(f"Analysis saved to: {output_path}")
        return output_path