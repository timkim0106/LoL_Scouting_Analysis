"""Abstract base classes for League of Legends entities."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class Ability(BaseModel):
    """Represents a champion ability."""
    
    name: str = Field(..., description="Ability name (Q, W, E, R, Passive)")
    physical_damage: float = Field(0.0, ge=0, description="Base physical damage")
    magic_damage: float = Field(0.0, ge=0, description="Base magic damage")
    ad_ratio: float = Field(0.0, ge=0, description="Attack damage scaling ratio")
    ap_ratio: float = Field(0.0, ge=0, description="Ability power scaling ratio")
    cooldown: Optional[float] = Field(None, ge=0, description="Cooldown in seconds")
    mana_cost: Optional[float] = Field(None, ge=0, description="Mana cost")
    
    # Special mechanics
    percent_max_hp_damage: float = Field(0.0, ge=0, description="Percent max HP damage")
    enhanced_by: Optional[str] = Field(None, description="Ability that enhances this one")
    enhancement_multiplier: float = Field(1.0, description="Damage multiplier when enhanced")
    is_melee_ability: bool = Field(True, description="Whether this is a melee-range ability")
    triggers_on_hit: bool = Field(False, description="Whether this triggers on-hit effects")
    stacks_modifier: float = Field(0.0, description="Damage per stack (for scaling abilities)")
    
    def calculate_damage(
        self,
        ad: float = 0,
        ap: float = 0,
        level: int = 1,
        ability_level: int = 1,
        target_max_hp: float = 3000,
        is_enhanced: bool = False,
        stacks: int = 0
    ) -> Dict[str, float]:
        """
        Calculate total damage from this ability.
        
        Args:
            ad: Total attack damage
            ap: Total ability power
            level: Champion level
            ability_level: Ability level
            target_max_hp: Target's maximum health
            is_enhanced: Whether ability is enhanced
            stacks: Number of stacks for scaling abilities
        
        Returns:
            Dictionary with physical, magic, and total damage
        """
        # Base damage calculations
        phys_dmg = self.physical_damage + (ad * self.ad_ratio)
        magic_dmg = self.magic_damage + (ap * self.ap_ratio)
        
        # Add percent max HP damage
        if self.percent_max_hp_damage > 0:
            hp_damage = target_max_hp * self.percent_max_hp_damage
            magic_dmg += hp_damage
        
        # Apply enhancement multiplier
        if is_enhanced and self.enhancement_multiplier != 1.0:
            phys_dmg *= self.enhancement_multiplier
            magic_dmg *= self.enhancement_multiplier
        
        # Add stack-based damage
        if stacks > 0 and self.stacks_modifier > 0:
            stack_damage = stacks * self.stacks_modifier
            magic_dmg += stack_damage  # Most stack-based damage is magic
        
        return {
            "physical": phys_dmg,
            "magic": magic_dmg,
            "total": phys_dmg + magic_dmg
        }


class ItemEffect(BaseModel):
    """Represents an item's stat effects."""
    
    attack_damage: float = Field(0.0, description="Attack damage bonus")
    ability_power: float = Field(0.0, description="Ability power bonus")
    health: float = Field(0.0, description="Health bonus")
    mana: float = Field(0.0, description="Mana bonus")
    armor: float = Field(0.0, description="Armor bonus")
    magic_resist: float = Field(0.0, description="Magic resistance bonus")
    attack_speed: float = Field(0.0, description="Attack speed bonus")
    crit_chance: float = Field(0.0, ge=0, le=1, description="Critical strike chance")
    crit_damage: float = Field(0.0, description="Critical strike damage multiplier")
    lethality: float = Field(0.0, description="Lethality (flat armor penetration)")
    armor_pen_percent: float = Field(0.0, ge=0, le=1, description="Percent armor penetration")
    magic_pen_flat: float = Field(0.0, description="Flat magic penetration")
    magic_pen_percent: float = Field(0.0, ge=0, le=1, description="Percent magic penetration")
    ability_haste: float = Field(0.0, description="Ability haste bonus")
    
    # Special passive effects
    eclipse_proc: bool = Field(False, description="Has Eclipse passive")
    muramana_shock: bool = Field(False, description="Has Muramana Shock passive")
    spellblade_proc: bool = Field(False, description="Has Spellblade passive")
    lich_bane_proc: bool = Field(False, description="Has Lich Bane passive")
    omnivamp: float = Field(0.0, description="Omnivamp healing ratio")
    movement_speed: float = Field(0.0, description="Movement speed bonus")
    on_hit_magic_damage: float = Field(0.0, description="On-hit magic damage")
    on_hit_ap_ratio: float = Field(0.0, description="On-hit damage AP scaling ratio")
    spellblade_ap_ratio: float = Field(0.0, description="Spellblade AP scaling ratio")
    mana_to_ad_ratio: float = Field(0.0, description="Mana to AD conversion ratio")


class ChampionStats(BaseModel):
    """Base stats for a champion at a specific level."""
    
    level: int = Field(1, ge=1, le=18, description="Champion level")
    health: float = Field(..., gt=0, description="Current health")
    mana: float = Field(0.0, ge=0, description="Current mana")
    attack_damage: float = Field(..., gt=0, description="Base attack damage")
    ability_power: float = Field(0.0, ge=0, description="Ability power")
    armor: float = Field(..., ge=0, description="Armor")
    magic_resist: float = Field(..., ge=0, description="Magic resistance")
    attack_speed: float = Field(..., gt=0, description="Attack speed")
    movement_speed: float = Field(..., gt=0, description="Movement speed")
    crit_chance: float = Field(0.0, ge=0, le=1, description="Critical strike chance")


class BaseChampion(ABC, BaseModel):
    """Abstract base class for all champions."""
    
    name: str = Field(..., description="Champion name")
    base_stats: Dict[int, ChampionStats] = Field(..., description="Stats by level")
    abilities: Dict[str, Ability] = Field(..., description="Champion abilities")
    
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"  # Allow extra fields for champion-specific attributes
    
    @abstractmethod
    def get_stats_at_level(self, level: int) -> ChampionStats:
        """Get champion stats at specified level."""
        pass
    
    @abstractmethod
    def calculate_combo_damage(
        self,
        combo: List[str],
        level: int,
        items: List["Item"],
        target_armor: float = 0,
        target_mr: float = 0
    ) -> Dict[str, float]:
        """Calculate damage for a specific ability combo."""
        pass
    
    def get_ability(self, ability_name: str) -> Ability:
        """Get ability by name."""
        if ability_name not in self.abilities:
            raise ValueError(f"Ability '{ability_name}' not found for {self.name}")
        return self.abilities[ability_name]


class BaseItem(ABC, BaseModel):
    """Abstract base class for all items."""
    
    name: str = Field(..., description="Item name")
    cost: int = Field(..., ge=0, description="Item cost in gold")
    effects: ItemEffect = Field(..., description="Item stat effects")
    
    @abstractmethod
    def apply_effects(self, champion_stats: ChampionStats) -> ChampionStats:
        """Apply item effects to champion stats."""
        pass
    
    @property
    def gold_efficiency(self) -> float:
        """Calculate gold efficiency of the item."""
        # This would need to be implemented with current stat values
        return 1.0