"""Item model implementations."""

from typing import Optional
from pydantic import Field

from .base import BaseItem, ItemEffect, ChampionStats


class Item(BaseItem):
    """Concrete implementation of an item."""
    
    def apply_effects(self, champion_stats: ChampionStats) -> ChampionStats:
        """Apply item effects to champion stats."""
        return ChampionStats(
            level=champion_stats.level,
            health=champion_stats.health + self.effects.health,
            mana=champion_stats.mana + self.effects.mana,
            attack_damage=champion_stats.attack_damage + self.effects.attack_damage,
            ability_power=champion_stats.ability_power + self.effects.ability_power,
            armor=champion_stats.armor + self.effects.armor,
            magic_resist=champion_stats.magic_resist + self.effects.magic_resist,
            attack_speed=champion_stats.attack_speed * (1 + self.effects.attack_speed),
            movement_speed=champion_stats.movement_speed,
            crit_chance=min(1.0, champion_stats.crit_chance + self.effects.crit_chance)
        )


# Pre-defined items for common builds
ESSENCE_REAVER = Item(
    name="Essence Reaver",
    cost=2900,
    effects=ItemEffect(
        attack_damage=60,
        ability_haste=15,
        crit_chance=0.25,
        ability_power=0,
        mana=0  # No mana, has mana restoration passive
    )
)

TRINITY_FORCE = Item(
    name="Trinity Force",
    cost=3333,
    effects=ItemEffect(
        attack_damage=36,
        ability_haste=15,
        health=333,
        mana=0,  # No mana in current version
        attack_speed=0.30,
        crit_chance=0.0,  # No crit in current version
        spellblade_proc=True  # Enables Spellblade passive
    )
)

MURAMANA = Item(
    name="Muramana",
    cost=2900,
    effects=ItemEffect(
        attack_damage=35,  # Base AD, gets +17.2 from Awe passive
        ability_haste=15,
        mana=860,
        mana_to_ad_ratio=0.02,  # 2% of max mana as bonus AD
        muramana_shock=True  # Enables Shock passive
    )
)

SPEAR_OF_SHOJIN = Item(
    name="Spear of Shojin",
    cost=3100,
    effects=ItemEffect(
        attack_damage=45,
        ability_haste=25,  # 25 basic ability haste
        health=450
    )
)

ECLIPSE = Item(
    name="Eclipse",
    cost=2900,
    effects=ItemEffect(
        attack_damage=60,
        ability_haste=15,
        lethality=0,  # No lethality in current version
        armor_pen_percent=0.0,  # No armor pen, has % max HP damage passive
        eclipse_proc=True  # Enables Eclipse passive
    )
)

SERYLDA_GRUDGE = Item(
    name="Serylda's Grudge",
    cost=3000,
    effects=ItemEffect(
        attack_damage=45,
        ability_haste=15,
        armor_pen_percent=0.35  # 35% armor penetration
    )
)

LORD_DOMINIKS = Item(
    name="Lord Dominik's Regards",
    cost=3100,
    effects=ItemEffect(
        attack_damage=35,
        crit_chance=0.25,
        armor_pen_percent=0.40  # 40% armor penetration
    )
)

# Item sets for easy access
ITEM_SETS = {
    "Eclipse_Muramana_Serylda": [ECLIPSE, MURAMANA, SERYLDA_GRUDGE],
    "Eclipse_Muramana_LDR": [ECLIPSE, MURAMANA, LORD_DOMINIKS],
    "ER_Trinity_Muramana": [ESSENCE_REAVER, TRINITY_FORCE, MURAMANA],
    "ER_Trinity_Shojin": [ESSENCE_REAVER, TRINITY_FORCE, SPEAR_OF_SHOJIN],
}