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


class Gwen(Champion):
    """Gwen champion implementation with Thousand Cuts passive."""
    
    def __init__(self, **kwargs):
        # Gwen base stats from wiki: 63 + 3 per level AD
        attack_damage_by_level = [63 + i * 3 for i in range(18)]
        
        # Create base stats with accurate wiki data: 600 + 110 HP, 330 + 40 mana, 36 + 4.9 armor, 32 + 2.05 MR
        base_stats = {}
        for lvl in range(1, 19):
            base_stats[lvl] = ChampionStats(
                level=lvl,
                health=600 + (lvl - 1) * 110,
                mana=330 + (lvl - 1) * 40,
                attack_damage=attack_damage_by_level[lvl - 1],
                ability_power=0,
                armor=36 + (lvl - 1) * 4.9,
                magic_resist=32 + (lvl - 1) * 2.05,
                attack_speed=0.69,  # Base attack speed
                movement_speed=340,
                crit_chance=0.0
            )
        
        # Define abilities with Thousand Cuts mechanics
        abilities = {
            "A": Ability(
                name="A", 
                physical_damage=0, 
                magic_damage=0,
                ad_ratio=1.0,
                ap_ratio=0.0,
                triggers_on_hit=True,
                percent_max_hp_damage=0.01  # 1% max HP base + 0.55% per 100 AP
            ),
            "Q": Ability(
                name="Q", 
                physical_damage=0,
                magic_damage=160,  # Final snip damage at max rank (60-160)
                ad_ratio=0.0, 
                ap_ratio=0.35,  # 35% AP for final snip
                triggers_on_hit=False,
                is_melee_ability=False
            ),
            "W": Ability(
                name="W", 
                physical_damage=0,
                magic_damage=0,  # Utility spell
                ad_ratio=0.0, 
                ap_ratio=0.0
            ),
            "E": Ability(
                name="E", 
                physical_damage=0,
                magic_damage=20,  # On-hit magic damage at max rank (8-20)
                ad_ratio=0.0, 
                ap_ratio=0.0,
                triggers_on_hit=True
            ),
            "R": Ability(
                name="R", 
                physical_damage=0,
                magic_damage=90,  # Per needle at max rank (30-90)
                ad_ratio=0.0, 
                ap_ratio=0.20  # 20% AP per needle
            )
        }
        
        super().__init__(
            name="Gwen",
            base_stats=base_stats,
            abilities=abilities,
            **kwargs
        )
    
    def calculate_thousand_cuts_damage(self, ap: float, target_max_hp: float) -> float:
        """Calculate Thousand Cuts passive damage."""
        base_percent = 0.01  # 1%
        ap_scaling = ap * 0.0055  # 0.55% per 100 AP
        total_percent = base_percent + ap_scaling
        return target_max_hp * total_percent
    
    def calculate_thousand_cuts_healing(self, thousand_cuts_damage: float, level: int) -> float:
        """Calculate healing from Thousand Cuts against champions."""
        # Healing scales from 10-25 based on level (capped)
        max_heal = 10 + (level - 1) * (15 / 17)  # Linear scaling from level 1-18
        raw_heal = thousand_cuts_damage * 0.5  # 50% of damage
        return min(raw_heal, max_heal)
    
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
        """Override to include Thousand Cuts mechanics and item effects."""
        # Get base damage calculation
        base_result = super().calculate_combo_damage(
            combo, level, items, target_armor, target_mr, target_health
        )
        
        # Calculate total AP from items
        stats = self.get_stats_at_level(level)
        total_ap = stats.ability_power
        total_ad = stats.attack_damage
        for item in items:
            total_ap += item.effects.ability_power
            total_ad += item.effects.attack_damage
        
        # Add Thousand Cuts damage to abilities and autos that trigger on-hit
        thousand_cuts_per_hit = self.calculate_thousand_cuts_damage(total_ap, target_health)
        thousand_cuts_hits = sum(1 for ability_name in combo 
                               if self.get_ability(ability_name).triggers_on_hit or ability_name in ["Q", "R"])
        
        total_thousand_cuts_damage = thousand_cuts_per_hit * thousand_cuts_hits
        
        # Add item on-hit effects (Nashor's Tooth)
        on_hit_damage = 0
        spellblade_damage = 0
        spellblade_used = False
        
        for ability_name in combo:
            ability = self.get_ability(ability_name)
            
            # Nashor's Tooth on-hit for basic attacks and on-hit abilities
            if ability.triggers_on_hit:
                for item in items:
                    if item.effects.on_hit_magic_damage > 0:
                        item_on_hit = item.effects.on_hit_magic_damage + (total_ap * item.effects.on_hit_ap_ratio)
                        on_hit_damage += item_on_hit
            
            # Lich Bane Spellblade (first ability triggers, next auto consumes)
            if not spellblade_used and ability_name not in ["A"] and any(item.effects.lich_bane_proc for item in items):
                # Find next auto attack in combo after this ability
                current_index = combo.index(ability_name)
                for next_ability in combo[current_index + 1:]:
                    if next_ability == "A":
                        for item in items:
                            if item.effects.lich_bane_proc:
                                spellblade_dmg = (total_ad * 0.75) + (total_ap * item.effects.spellblade_ap_ratio)
                                spellblade_damage += spellblade_dmg
                                spellblade_used = True
                                break
                        break
        
        # Calculate healing (only against champions)
        total_healing = self.calculate_thousand_cuts_healing(total_thousand_cuts_damage, level)
        
        # Apply MR to all magic damage
        effective_mr = target_mr
        for item in items:
            if item.effects.magic_pen_percent > 0:
                effective_mr *= (1 - item.effects.magic_pen_percent)
            if item.effects.magic_pen_flat > 0:
                effective_mr -= item.effects.magic_pen_flat
        effective_mr = max(0, effective_mr)
        
        # Apply resistances
        thousand_cuts_dealt = total_thousand_cuts_damage * 100 / (100 + effective_mr)
        on_hit_dealt = on_hit_damage * 100 / (100 + effective_mr)
        spellblade_dealt = spellblade_damage * 100 / (100 + effective_mr)
        
        # Add all bonus magic damage
        total_bonus_magic_raw = total_thousand_cuts_damage + on_hit_damage + spellblade_damage
        total_bonus_magic_dealt = thousand_cuts_dealt + on_hit_dealt + spellblade_dealt
        
        base_result["raw_magic"] += total_bonus_magic_raw
        base_result["raw_total"] += total_bonus_magic_raw
        base_result["magic_dealt"] += total_bonus_magic_dealt
        base_result["total_dealt"] += total_bonus_magic_dealt
        
        # Add detailed effect info
        base_result["special_effects"]["thousand_cuts_damage"] = total_thousand_cuts_damage
        base_result["special_effects"]["thousand_cuts_healing"] = total_healing
        base_result["special_effects"]["thousand_cuts_hits"] = thousand_cuts_hits
        base_result["special_effects"]["nashors_on_hit_damage"] = on_hit_damage
        base_result["special_effects"]["lich_bane_spellblade_damage"] = spellblade_damage
        
        return base_result