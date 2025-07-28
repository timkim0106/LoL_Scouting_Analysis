"""Statistical analysis module for League of Legends data."""

import numpy as np
from typing import Dict, List, Any


class StatisticalAnalyzer:
    """Statistical analysis tools for League of Legends performance data."""
    
    def __init__(self):
        """Initialize the statistical analyzer."""
        pass
    
    def calculate_confidence_interval(
        self, 
        data: List[float], 
        confidence: float = 0.95
    ) -> Dict[str, float]:
        """
        Calculate confidence interval for damage data.
        
        Args:
            data: List of damage values
            confidence: Confidence level (default 95%)
        
        Returns:
            Dictionary with confidence interval bounds
        """
        data_array = np.array(data)
        mean = np.mean(data_array)
        std = np.std(data_array)
        n = len(data_array)
        
        # Calculate margin of error
        z_score = 1.96 if confidence == 0.95 else 2.576  # 95% or 99%
        margin_error = z_score * (std / np.sqrt(n))
        
        return {
            "mean": mean,
            "lower_bound": mean - margin_error,
            "upper_bound": mean + margin_error,
            "margin_error": margin_error
        }
    
    def analyze_damage_variance(
        self, 
        damage_data: List[float]
    ) -> Dict[str, float]:
        """
        Analyze variance in damage calculations.
        
        Args:
            damage_data: List of damage values
        
        Returns:
            Statistical summary
        """
        data_array = np.array(damage_data)
        
        return {
            "mean": np.mean(data_array),
            "median": np.median(data_array),
            "std": np.std(data_array),
            "variance": np.var(data_array),
            "min": np.min(data_array),
            "max": np.max(data_array),
            "coefficient_of_variation": np.std(data_array) / np.mean(data_array)
        }