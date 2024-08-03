import numpy as np
import matplotlib.pyplot as plt

# shyvana attack damage level 1 to 18 (1 indexed)
shyvana_attack_damage = [0, 66, 68.16, 70.43, 72.8, 75.27, 77.85, 80.54,
                         83.33, 86.22, 89.22, 92.33, 95.54, 98.85, 
                         102.27, 105.8, 109.43, 113.16, 117]


# Champion abilities Shyvana lv 13
# W damage is per tick, 
# E1 is patch 14.14, E2 is patch 14.15
# RE is dragon form E
abilities13 = {
    'A': {'physical_damage': shyvana_attack_damage[12], 'magic_damage': 0, 'ad_ratio': 1, 'ap_ratio': 0},
    'Q': {'physical_damage': shyvana_attack_damage[12] , 'magic_damage': 0, 'ad_ratio': 1.2, 'ap_ratio': .75},
    'W': {'physical_damage': 0, 'magic_damage': 30, 'ad_ratio': .1, 'ap_ratio': 0},
    'WA': {'physical_damage': shyvana_attack_damage[12], 'magic_damage': 13, 'ad_ratio': 0.05, 'ap_ratio': 0},
    'E1': {'physical_damage': 0,'magic_damage': 220, 'ad_ratio': .4, 'ap_ratio': .9},
    'E2': {'physical_damage': 0,'magic_damage': 245, 'ad_ratio': .5, 'ap_ratio': .8},
    'RE1': {'physical_damage': 0, 'magic_damage': 330, 'ad_ratio': .7, 'ap_ratio': 1.2},
    'RE2': {'physical_damage': 0,'magic_damage': 355, 'ad_ratio': 1, 'ap_ratio': 1}, #bonus ad ratio
    'R': {'physical_damage': 0,'magic_damage': 0, 'ad_ratio': 1.75, 'ap_ratio': 0},
    'RT1': {'physical_damage': 0,'magic_damage': 47.5, 'ad_ratio': .05, 'ap_ratio': 0},
    'RT2': {'physical_damage': 0,'magic_damage': 47.5, 'ad_ratio': .15, 'ap_ratio': 0} # bonus ad ratio
}


def abilityE1Damage(level, ELevel, itemsAD, itemsAP):
  
    baseDamage = 20 + 40 * ELevel
    adBonusDamage = .4 * (shyvana_attack_damage[level] + itemsAD)
    apBonusDamage = .9 * itemsAP
    totalDamage = baseDamage + adBonusDamage + apBonusDamage
    return totalDamage


def abilityE2Damage(level, ELevel, itemsAD, itemsAP):
    baseDamage = 45 + 40 * ELevel
    adBonusDamage = .5 * itemsAD
    apBonusDamage = .8 * itemsAP
    totalDamage = baseDamage + adBonusDamage + apBonusDamage
    return totalDamage


def abilityRE1Damage(level, ELevel, itemsAD, itemsAP):
    if level <= 6:
        baseDamage = 20 + 40 * ELevel + 75
    else:
        baseDamage = 20 + 40 * ELevel + 5 * (level - 6)
    adBonusDamage = 1.1 * (shyvana_attack_damage[level] + itemsAD)
    apBonusDamage = 2.1 * itemsAP
    totalDamage = baseDamage + adBonusDamage + apBonusDamage
    return totalDamage
    
def abilityRE2Damage(level, ELevel, itemsAD, itemsAP):
    if level <= 6:
        baseDamage = 45 + 40 * ELevel + 75
    else:
        baseDamage = 45 + 40 * ELevel + 5 * (level - 6)
    adBonusDamage = (shyvana_attack_damage[level] + itemsAD) + .5 * itemsAD
    apBonusDamage = 1.8 * itemsAP
    totalDamage = baseDamage + adBonusDamage + apBonusDamage
    return totalDamage


pre0 = abilityE1Damage(1, 1, 0, 0)
post0 = abilityE2Damage(1, 1, 0, 0)
print(pre0 - post0)

pre1 = abilityE1Damage(5, 3, 25, 15)
post1 = abilityE2Damage(5, 3, 25, 15)


pre2 = abilityE1Damage(7, 4, 45, 15)
post2 = abilityE2Damage(7, 4, 45, 15)

print (pre1 - post1)
print(pre2 - post2)


pre3 = abilityE1Damage(9, 5, 55, 30)
post3 = abilityE2Damage(9, 5, 55, 30)
print(pre3 - post3)


preR1 = abilityRE1Damage(6, 3, 35, 15)
postR1 = abilityRE2Damage(6, 3, 35, 15)
print (preR1 - postR1)


preR2 = abilityRE1Damage(11, 5, 55, 175)
postR2 = abilityRE2Damage(11, 5, 55, 175)
print ( preR2 - postR2)
damage1 = ['E1']
damage2 = ['E2']