"""
League of Legends Analytics Package

A comprehensive analytics framework for League of Legends performance analysis,
champion damage calculations, and professional player tracking.
"""

__version__ = "1.0.0"
__author__ = "Timothy Kim"

from .core import ChampionAnalyzer, PlayerTracker
from .models import Champion, Item, Player

__all__ = [
    "ChampionAnalyzer",
    "PlayerTracker", 
    "Champion",
    "Item",
    "Player",
]