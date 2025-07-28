"""Champion model implementations."""

from typing import Dict, List, Optional
from pydantic import Field

from .base import BaseChampion, ChampionStats, Ability


class Champion(BaseChampion):
    """Concrete implementation of a champion."""
    
    def get_stats_at_level(self, level: int) -> ChampionStats:
        """Get champion stats at specified level."""
        if level not in self.base_stats:
            raise ValueError(f"Stats not available for level {level}")
        return self.base_stats[level]
    
    def calculate_combo_damage(
        self,
        combo: List[str],
        level: int,
        items: List["Item"],
        target_armor: float = 0,
        target_mr: float = 0,
        target_health: float = 3000,
        dragon_practice_stacks: Optional[int] = None
    ) -> Dict[str, float]:
        stats = self.get_stats_at_level(level)
        
        total_ad = stats.attack_damage
        total_ap = stats.ability_power
        total_mana = stats.mana
        
        has_eclipse = False
        has_muramana = False
        has_spellblade = False
        eclipse_proc_count = 0
        muramana_bonus_ad = 0
        
        for item in items:
            total_ad += item.effects.attack_damage
            total_ap += item.effects.ability_power
            total_mana += item.effects.mana
            
            # Muramana Awe passive: bonus AD from mana
            if item.effects.mana_to_ad_ratio > 0:
                muramana_bonus_ad = (total_mana + item.effects.mana) * item.effects.mana_to_ad_ratio
                total_ad += muramana_bonus_ad
            
            # Track special passives
            if item.effects.eclipse_proc:
                has_eclipse = True
            if item.effects.muramana_shock:
                has_muramana = True
            if item.effects.spellblade_proc:
                has_spellblade = True
        
        total_physical_damage = 0.0
        total_magic_damage = 0.0
        ability_hit_count = 0
        
        # Get Dragon Practice stacks for Smolder
        stacks = getattr(self, 'dragon_practice_stacks', dragon_practice_stacks or 0)
        
        for ability_name in combo:
            ability = self.get_ability(ability_name)
            ability_hit_count += 1
            
            # Check for Jayce E1Q1 enhancement
            is_enhanced = ability_name == "E1Q1" or (ability.enhanced_by and ability.enhanced_by in combo)
            
            damage = ability.calculate_damage(
                ad=total_ad,
                ap=total_ap,
                level=level,
                target_max_hp=target_health,
                is_enhanced=is_enhanced,
                stacks=stacks
            )
            
            base_physical = damage["physical"]
            base_magic = damage["magic"]
            
            # Apply Muramana Shock passive
            if has_muramana and ability_name not in ["A", "WA", "W1A"]:  # Abilities, not basic attacks
                shock_damage_percent = 0.04 if ability.is_melee_ability else 0.03  # 4% melee, 3% ranged
                shock_damage = total_mana * shock_damage_percent
                base_physical += shock_damage
            
            # Apply Eclipse passive (every 2 hits)
            if has_eclipse and ability_hit_count % 2 == 0:
                eclipse_damage_percent = 0.06 if ability.is_melee_ability else 0.04  # 6% melee, 4% ranged
                eclipse_damage = target_health * eclipse_damage_percent
                base_physical += eclipse_damage
                eclipse_proc_count += 1
            
            # Apply Spellblade (Trinity Force) - 200% base AD on first ability
            if has_spellblade and ability_hit_count == 1:
                spellblade_damage = stats.attack_damage * 2.0  # 200% base AD
                base_physical += spellblade_damage
            
            total_physical_damage += base_physical
            total_magic_damage += base_magic
        
        # Apply armor penetration from items
        effective_armor = target_armor
        effective_mr = target_mr
        
        for item in items:
            if item.effects.armor_pen_percent > 0:
                effective_armor *= (1 - item.effects.armor_pen_percent)
            if item.effects.lethality > 0:
                effective_armor -= item.effects.lethality
            if item.effects.magic_pen_percent > 0:
                effective_mr *= (1 - item.effects.magic_pen_percent)
            if item.effects.magic_pen_flat > 0:
                effective_mr -= item.effects.magic_pen_flat
        
        effective_armor = max(0, effective_armor)
        effective_mr = max(0, effective_mr)
        
        # Calculate damage after resistances
        physical_damage_dealt = total_physical_damage * 100 / (100 + effective_armor)
        magic_damage_dealt = total_magic_damage * 100 / (100 + effective_mr)
        
        return {
            "raw_physical": total_physical_damage,
            "raw_magic": total_magic_damage,
            "raw_total": total_physical_damage + total_magic_damage,
            "physical_dealt": physical_damage_dealt,
            "magic_dealt": magic_damage_dealt,
            "total_dealt": physical_damage_dealt + magic_damage_dealt,
            "special_effects": {
                "eclipse_procs": eclipse_proc_count,
                "muramana_bonus_ad": muramana_bonus_ad,
                "effective_armor": effective_armor,
                "effective_mr": effective_mr,
                "dragon_practice_stacks": stacks
            }
        }


class Smolder(Champion):
    """Smolder champion implementation with Dragon Practice stacking system."""
    
    def __init__(self, level: int = 13, dragon_practice_stacks: int = 100, **kwargs):
        """Initialize Smolder with default stats."""
        
        # Accurate base stats from wiki: 60 (+2.3 per level)
        attack_damage_by_level = {}
        for lvl in range(1, 19):
            attack_damage_by_level[lvl] = 60 + (lvl - 1) * 2.3
        
        # Accurate mana: 300 (+40 per level)
        mana_by_level = {}
        for lvl in range(1, 19):
            mana_by_level[lvl] = 300 + (lvl - 1) * 40
        
        # Create base stats with accurate wiki data: 575 (+100 HP), 24 (+4.7 armor), 30 (+1.3 MR)
        base_stats = {}
        for lvl in range(1, 19):
            base_stats[lvl] = ChampionStats(
                level=lvl,
                health=575 + (lvl - 1) * 100,
                mana=mana_by_level[lvl],
                attack_damage=attack_damage_by_level[lvl],
                ability_power=0,
                armor=24 + (lvl - 1) * 4.7,
                magic_resist=30 + (lvl - 1) * 1.3,
                attack_speed=0.625,
                movement_speed=330,  # Wiki shows 330
                crit_chance=0.0
            )
        
        # Define abilities with Dragon Practice stacking mechanics
        abilities = {
            "Q": Ability(
                name="Q",
                physical_damage=125,  # Max rank: 65/80/95/110/125
                magic_damage=0,
                ad_ratio=1.30,  # 130% bonus AD
                ap_ratio=0.0,
                stacks_modifier=0.55,  # ~40-70% of stacks as bonus damage
                triggers_on_hit=False
            ),
            "W": Ability(
                name="W",
                physical_damage=0,
                magic_damage=100,  # Glob damage at max rank
                ad_ratio=0.60,   # 60% bonus AD for glob
                ap_ratio=0.0,
                stacks_modifier=0.55,  # 55% of stacks as bonus damage
                triggers_on_hit=False
            ),
            "E": Ability(
                name="E",
                physical_damage=30,  # Bolt damage at max rank: 10/15/20/25/30
                magic_damage=0,
                ad_ratio=0.30,   # 30% AD per bolt
                ap_ratio=0.0,
                stacks_modifier=0.12,  # 12% of stacks as bonus damage
                triggers_on_hit=False
            ),
            "R": Ability(
                name="R",
                physical_damage=0,
                magic_damage=400,  # Max rank: 200/300/400
                ad_ratio=1.10,   # 110% bonus AD
                ap_ratio=1.0,    # 100% AP
                stacks_modifier=0.0  # R doesn't scale with stacks
            ),
            "A": Ability(
                name="A",
                physical_damage=0,
                magic_damage=0,
                ad_ratio=1.0,
                ap_ratio=0.0,
                triggers_on_hit=True
            )
        }
        
        super().__init__(
            name="Smolder",
            base_stats=base_stats,
            abilities=abilities,
            **kwargs
        )
        
        # Set Dragon Practice stacks after initialization
        self.dragon_practice_stacks = dragon_practice_stacks


class Jayce(Champion):
    """Jayce champion implementation."""
    
    def __init__(self, **kwargs):
        # Jayce attack damage level 1 to 18
        attack_damage_by_level = [
            59, 62.06, 65.27, 68.63, 72.13, 75.79, 79.59, 83.54,
            87.65, 91.9, 96.29, 100.84, 105.54, 110.38, 115.38,
            120.52, 125.81, 131.25
        ]
        
        # Create base stats (accurate wiki data)
        base_stats = {}
        for lvl in range(1, 19):
            base_stats[lvl] = ChampionStats(
                level=lvl,
                health=590 + (lvl - 1) * 109,
                mana=375 + (lvl - 1) * 45,
                attack_damage=attack_damage_by_level[lvl - 1],
                ability_power=0,
                armor=22 + (lvl - 1) * 5,
                magic_resist=30 + (lvl - 1) * 1.3,
                attack_speed=0.658,
                movement_speed=335,
                crit_chance=0.0
            )
        
        # Define abilities with enhancement mechanics
        abilities = {
            "A": Ability(
                name="A", 
                physical_damage=0, 
                ad_ratio=1.0, 
                triggers_on_hit=True
            ),
            "Q1": Ability(
                name="Q1", 
                physical_damage=310, 
                ad_ratio=1.40,  # Cannon Q max rank
                enhanced_by="E1",
                enhancement_multiplier=1.40,  # 40% bonus when accelerated
                is_melee_ability=False
            ),
            "Q2": Ability(
                name="Q2", 
                physical_damage=285, 
                ad_ratio=1.35,   # Hammer Q max rank
                is_melee_ability=True
            ),
            "W1A": Ability(
                name="W1A", 
                physical_damage=0, 
                ad_ratio=1.10,   # Cannon W enhanced auto
                triggers_on_hit=True,
                is_melee_ability=False
            ),
            "W2": Ability(
                name="W2", 
                magic_damage=440, 
                ap_ratio=0.0,      # Hammer W total damage
                is_melee_ability=True
            ),
            "E1Q1": Ability(
                name="E1Q1", 
                physical_damage=434, 
                ad_ratio=1.96,  # Pre-calculated enhanced Q
                is_melee_ability=False
            ),
            "E2": Ability(
                name="E2", 
                physical_damage=0, 
                ad_ratio=0.0,     
                percent_max_hp_damage=0.22,  # 22% max HP at max rank
                is_melee_ability=True
            ),
            "R1": Ability(
                name="R1", 
                magic_damage=0, 
                ad_ratio=0.0        # Transform ability
            ),
            "R2": Ability(
                name="R2", 
                physical_damage=0, 
                ad_ratio=0.0      # Armor/MR reduction passive
            )
        }
        
        super().__init__(
            name="Jayce",
            base_stats=base_stats,
            abilities=abilities,
            **kwargs
        )


class Shyvana(Champion):
    """Shyvana champion implementation."""
    
    def __init__(self, **kwargs):
        # Accurate Shyvana AD from wiki: 66 (+3 per level)
        attack_damage_by_level = [66 + i * 3 for i in range(18)]
        
        # Create base stats with accurate wiki data: 665 (+104 HP), 38 (+4.55 armor), 32 (+1.5 MR)
        base_stats = {}
        for lvl in range(1, 19):
            base_stats[lvl] = ChampionStats(
                level=lvl,
                health=665 + (lvl - 1) * 104,
                mana=100,  # Fury system
                attack_damage=attack_damage_by_level[lvl - 1],
                ability_power=0,
                armor=38 + (lvl - 1) * 4.55,
                magic_resist=32 + (lvl - 1) * 1.5,
                attack_speed=0.658,
                movement_speed=350,
                crit_chance=0.0
            )
        
        # Define abilities with on-hit mechanics
        abilities = {
            "A": Ability(
                name="A", 
                physical_damage=0, 
                ad_ratio=1.0, 
                triggers_on_hit=True
            ),
            "Q": Ability(
                name="Q", 
                physical_damage=0, 
                ad_ratio=1.0, 
                ap_ratio=0.50,  # 100% AD + 50% AP
                triggers_on_hit=True  # Twin Bite applies on-hit
            ),
            "W": Ability(
                name="W", 
                magic_damage=30, 
                ad_ratio=0.10  # Per tick: 10/15/20/25/30 (+10% bonus AD)
            ),
            "WA": Ability(
                name="WA", 
                physical_damage=0, 
                magic_damage=13, 
                ad_ratio=0.05,  # On-hit bonus
                triggers_on_hit=True
            ),
            "E": Ability(
                name="E", 
                magic_damage=245, 
                ad_ratio=0.50, 
                ap_ratio=0.70,  # Max: 85/125/165/205/245 (+50% bonus AD)(+70% AP)
                percent_max_hp_damage=0.03  # 3% max HP on-hit
            ),
            "RE": Ability(
                name="RE", 
                magic_damage=300, 
                ad_ratio=0.60, 
                ap_ratio=0.80  # Dragon form enhanced
            ),
            "R": Ability(
                name="R", 
                physical_damage=0, 
                ad_ratio=0.0  # Transformation ability
            ),
            "W_TICK": Ability(
                name="W_TICK", 
                magic_damage=30, 
                ad_ratio=0.10  # Individual tick
            )
        }
        
        super().__init__(
            name="Shyvana",
            base_stats=base_stats,
            abilities=abilities,
            **kwargs
        )