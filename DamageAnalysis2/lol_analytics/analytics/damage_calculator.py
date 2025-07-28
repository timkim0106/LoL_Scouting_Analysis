"""Advanced damage calculation with statistical analysis."""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass

from ..models.champion import Champion
from ..models.item import Item
from ..utils.logger import logger


@dataclass
class DamageResult:
    """Container for damage calculation results."""
    
    raw_physical: float
    raw_magic: float
    raw_total: float
    physical_dealt: float
    magic_dealt: float
    total_dealt: float
    target_armor: float
    target_mr: float
    items_used: List[str]
    combo_used: List[str]


class DamageCalculator:
    """
    Advanced damage calculator with statistical analysis capabilities.
    """
    
    def __init__(self):
        """Initialize the damage calculator."""
        self.results_cache: Dict[str, DamageResult] = {}
    
    def calculate_damage_vs_armor_range(
        self,
        champion: Champion,
        combo: List[str],
        items: List[Item],
        level: int = 13,
        armor_range: Tuple[float, float] = (30, 200),
        armor_points: int = 100,
        target_mr: float = 70,
        target_health: float = 3000
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate damage across a range of armor values.
        
        Args:
            champion: Champion instance
            combo: List of ability names
            items: List of items
            level: Champion level
            armor_range: (min_armor, max_armor)
            armor_points: Number of data points
            target_mr: Target magic resistance
            target_health: Target health
        
        Returns:
            Tuple of (armor_values, damage_values)
        """
        armor_values = np.linspace(armor_range[0], armor_range[1], armor_points)
        damage_values = []
        
        for armor in armor_values:
            damage_result = champion.calculate_combo_damage(
                combo=combo,
                level=level,
                items=items,
                target_armor=armor,
                target_mr=target_mr,
                target_health=target_health
            )
            damage_values.append(damage_result["total_dealt"])
        
        return armor_values, np.array(damage_values)
    
    def compare_item_builds(
        self,
        champion: Champion,
        combo: List[str],
        item_builds: Dict[str, List[Item]],
        level: int = 13,
        armor_range: Tuple[float, float] = (30, 200),
        armor_points: int = 100,
        target_mr: float = 70
    ) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """
        Compare damage output of different item builds.
        
        Args:
            champion: Champion instance
            combo: List of ability names
            item_builds: Dictionary mapping build names to item lists
            level: Champion level
            armor_range: (min_armor, max_armor)
            armor_points: Number of data points
            target_mr: Target magic resistance
        
        Returns:
            Dictionary mapping build names to (armor_values, damage_values)
        """
        results = {}
        
        for build_name, items in item_builds.items():
            logger.info(f"Calculating damage for build: {build_name}")
            armor_values, damage_values = self.calculate_damage_vs_armor_range(
                champion=champion,
                combo=combo,
                items=items,
                level=level,
                armor_range=armor_range,
                armor_points=armor_points,
                target_mr=target_mr
            )
            results[build_name] = (armor_values, damage_values)
        
        return results
    
    def calculate_damage_differential(
        self,
        champion: Champion,
        combo: List[str],
        build1: List[Item],
        build2: List[Item],
        build1_name: str = "Build 1",
        build2_name: str = "Build 2",
        level: int = 13,
        armor_range: Tuple[float, float] = (30, 200),
        armor_points: int = 100,
        target_mr: float = 70
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate damage differential between two builds.
        
        Args:
            champion: Champion instance
            combo: List of ability names
            build1: First item build
            build2: Second item build
            build1_name: Name for first build
            build2_name: Name for second build
            level: Champion level
            armor_range: (min_armor, max_armor)
            armor_points: Number of data points
            target_mr: Target magic resistance
        
        Returns:
            Tuple of (armor_values, damage_differential)
        """
        armor_values, damage1 = self.calculate_damage_vs_armor_range(
            champion, combo, build1, level, armor_range, armor_points, target_mr
        )
        
        _, damage2 = self.calculate_damage_vs_armor_range(
            champion, combo, build2, level, armor_range, armor_points, target_mr
        )
        
        differential = damage1 - damage2
        
        logger.info(f"Calculated differential between {build1_name} and {build2_name}")
        logger.info(f"Max advantage: {np.max(differential):.1f} damage")
        logger.info(f"Min advantage: {np.min(differential):.1f} damage")
        
        return armor_values, differential
    
    def monte_carlo_damage_simulation(
        self,
        champion: Champion,
        combo: List[str],
        items: List[Item],
        level: int = 13,
        target_armor: float = 100,
        target_mr: float = 70,
        variance_percent: float = 0.1,
        iterations: int = 10000
    ) -> Dict[str, float]:
        """
        Run Monte Carlo simulation for damage variance analysis.
        
        Args:
            champion: Champion instance
            combo: List of ability names
            items: List of items
            level: Champion level
            target_armor: Target armor
            target_mr: Target magic resistance
            variance_percent: Variance as percentage of base values
            iterations: Number of simulation iterations
        
        Returns:
            Statistical summary of damage distribution
        """
        logger.info(f"Running Monte Carlo simulation with {iterations} iterations")
        
        damage_samples = []
        
        for _ in range(iterations):
            # Add random variance to stats
            varied_armor = target_armor * np.random.normal(1.0, variance_percent)
            varied_mr = target_mr * np.random.normal(1.0, variance_percent)
            
            # Ensure non-negative values
            varied_armor = max(0, varied_armor)
            varied_mr = max(0, varied_mr)
            
            damage_result = champion.calculate_combo_damage(
                combo=combo,
                level=level,
                items=items,
                target_armor=varied_armor,
                target_mr=varied_mr
            )
            
            damage_samples.append(damage_result["total_dealt"])
        
        damage_array = np.array(damage_samples)
        
        results = {
            "mean": np.mean(damage_array),
            "std": np.std(damage_array),
            "min": np.min(damage_array),
            "max": np.max(damage_array),
            "median": np.median(damage_array),
            "percentile_25": np.percentile(damage_array, 25),
            "percentile_75": np.percentile(damage_array, 75),
            "confidence_interval_95": (
                np.percentile(damage_array, 2.5),
                np.percentile(damage_array, 97.5)
            )
        }
        
        logger.info(f"Simulation complete. Mean damage: {results['mean']:.1f} ± {results['std']:.1f}")
        
        return results
    
    def plot_damage_comparison(
        self,
        comparison_data: Dict[str, Tuple[np.ndarray, np.ndarray]],
        title: str = "Damage Comparison",
        xlabel: str = "Target Armor",
        ylabel: str = "Damage Dealt",
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Create a plot comparing damage across different builds.
        
        Args:
            comparison_data: Data from compare_item_builds
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            save_path: Path to save the plot (optional)
        
        Returns:
            Matplotlib figure object
        """
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for i, (build_name, (armor_values, damage_values)) in enumerate(comparison_data.items()):
            color = colors[i % len(colors)]
            ax.plot(armor_values, damage_values, label=build_name, linewidth=2.5, color=color)
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # Add some styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to: {save_path}")
        
        return fig
    
    def plot_damage_differential(
        self,
        armor_values: np.ndarray,
        damage_differential: np.ndarray,
        build1_name: str = "Build 1",
        build2_name: str = "Build 2",
        title: Optional[str] = None,
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot damage differential between two builds.
        
        Args:
            armor_values: Armor values array
            damage_differential: Damage differential array
            build1_name: Name of first build
            build2_name: Name of second build
            title: Plot title (auto-generated if None)
            save_path: Path to save the plot (optional)
        
        Returns:
            Matplotlib figure object
        """
        if title is None:
            title = f"Damage Differential: {build1_name} vs {build2_name}"
        
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot the differential
        ax.plot(armor_values, damage_differential, linewidth=3, color='#2E86C1', label=f'{build1_name} - {build2_name}')
        
        # Add zero line
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.7, linewidth=1)
        
        # Fill areas
        ax.fill_between(armor_values, damage_differential, 0, 
                       where=(damage_differential > 0), alpha=0.3, color='green', 
                       label=f'{build1_name} Advantage')
        ax.fill_between(armor_values, damage_differential, 0, 
                       where=(damage_differential < 0), alpha=0.3, color='red',
                       label=f'{build2_name} Advantage')
        
        ax.set_xlabel("Target Armor", fontsize=12)
        ax.set_ylabel("Damage Differential", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # Styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Differential plot saved to: {save_path}")
        
        return fig