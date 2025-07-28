import numpy as np
import matplotlib.pyplot as plt


# ER Tri


# ER Shojin

# ER Manamune

# Tri Shojin

# Tri Manamune

# Shojin Manamune


# Smolder base AD lv 8 - 18
attackDamage = [73.28, 75.5, 77.8, 80.18, 82.64, 85.19, 87.81, 90.51, 93.29, 96.16, 99.1]

# Smolder base mana lv 13 - 18
mana = [738, 783.6, 830.6, 879, 928.8, 980]


muramana_mana = 860
muramana_ad_13 = .025*(mana[0] + muramana_mana)


items1 = ["Essence Reaver", "Trinity Force"]
items2 = ["Essence Reaver", "Muramana"]
items3 = ["Essence Reaver", "Shojin"]
items4 = ["Trinity Force", "Shojin"]
items5 = ["Trinity Force", "Muramana"]
items6 = ["Shojin", "Muramana"]


combo1 = ['Q']
combo2 = ['R', 'W', 'Q']
combo3 = ['R', 'W', 'A', 'Q']
combo4 = ['A', 'Q']
combo5 = ['W', 'A', 'Q']
combo6 = ['E']
class Smolder:

    def __init__(self):
        self.level = 13
        self.ad = attackDamage[5]
        self.mana = mana[0]
        self.items = []


    def __init__(self, level, items):
        self.level = level
        self.ad = attackDamage[level - 8]
        self.mana = mana[self.level - 13] if level >= 13 else 0 
        self.items = items


    def calculateDamage(combo, items):
        return combo 



    def calculateItems(items):
        dmg = ""
        for item in items:
            dmg += item
        return dmg

s1 = Smolder()
s2 = Smolder(14, items1)



