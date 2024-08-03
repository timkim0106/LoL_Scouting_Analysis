import numpy as np
import matplotlib.pyplot as plt

# this comment

# jayce attack damage level 1 to 18
jayce_attack_damage = [59, 62.06, 65.27, 68.63, 72.13, 75.79, 79.59, 83.54, 87.65, 91.9, 
                       96.29, 100.84, 105.54, 110.38, 115.38, 120.52, 125.81, 131.25]


# Champion abilities Jayce lv 13
# 1 is cannon form, 2 is hammer form
abilities13 = {
    'A': {'physical_damage': jayce_attack_damage[12], 'magic_damage': 0, 'ad_ratio': 1, 'ap_ratio': 0},
    'Q1': {'physical_damage': 335, 'magic_damage': 0, 'ad_ratio': 1.25, 'ap_ratio': 0},
    'Q2': {'physical_damage': 310, 'magic_damage': 0, 'ad_ratio': 1.2, 'ap_ratio': 0},
    'W1A': {'physical_damage': 1.1* jayce_attack_damage[12], 'magic_damage': 0, 'ad_ratio': 1.1, 'ap_ratio': 0},
    'W2': {'physical_damage': 0, 'magic_damage': 460, 'ad_ratio': 0, 'ap_ratio': 1},
    'E1Q1': {'physical_damage': 469,'magic_damage': 0, 'ad_ratio': 1.75, 'ap_ratio': 0},
    'E2': {'physical_damage': 0,'magic_damage': 0, 'ad_ratio': 1, 'ap_ratio': 0},
    'R1': {'physical_damage': 0, 'magic_damage': 105, 'ad_ratio': .25, 'ap_ratio': 0},
    'R2': {'physical_damage': 0,'magic_damage': 0, 'ad_ratio': 1.75, 'ap_ratio': 0}
}
#E2 max hp dmg
#R1 is cannon -> hammer enhanced auto
#R2 20% armor/mr reduction

# Jayce mana lv 13 - 18
mana = [867.75, 919.05, 971.93, 1026.38, 1082.4, 1140]

muramana_mana = 860
muramana_ad_13 = .025*(mana[0] + muramana_mana)


# Item sets Eclipse Muramana Serylda vs Eclipse Muramana LDR
item_sets_13 = {
    'Item Set 1': {'ad': 150 + muramana_ad_13, 'ap': 0, 'flat_armor_pen': 15, 'percent_armor_pen': .2665},
    'Item Set 2': {'ad': 150 + muramana_ad_13, 'ap': 0, 'flat_armor_pen': 0, 'percent_armor_pen': .4}
}




def calculate_damage(ability_list, items, health, armor, mr):
    
    total_damage = 0
    
    dmg_count = 0
    
    for ability in ability_list:
        
        specific = abilities13[ability]
        
        dmg_count = dmg_count + 1
        
        # armor/mr reduction from cannon auto
        if (specific == 'R2'):
            armor *= .8
            mr *= .8
            
        # max health damage from hammer E
        elif (specific == 'E2'):
            ap_damage = .08 * health + items['ad'] * specific['ad_ratio']
            
        # muramana bonus onhit
        elif ((specific == 'W1A') or (specific == 'A')):
            ad_damage = .015 * (mana[0] + muramana_mana) + specific['physical_damage'] + (items['ad'] * specific['ad_ratio'])
            
        else:
            ad_damage = specific['physical_damage'] + (items['ad'] * specific['ad_ratio'])
    
            ap_damage = specific['magic_damage'] + (items['ap'] * specific['ap_ratio'])
            
            
            # manamune bonus ability dmg
            ad_damage += .027 * (mana[0] + muramana_mana) + (items['ad'] * .06)
            
        # eclipse proc (assumed melee) 
        if (dmg_count == 2):
            ad_damage += .06 * health
            
    
    # Calculate effective resistance considering penetration
    # flat armor reduction -> % armor reduction -> % armor pen -> flat armor pen
    # armor/mr reduction alrdy occured in R2 calculation (only reduction calculation needed)
    
        effective_armor = armor * (1 - items['percent_armor_pen']) - items['flat_armor_pen']
        physical_damage_taken = ad_damage * 100 / (100 + effective_armor)
    
    # not considering magic pen (Jayce gets 0)
        # effective_mr = mr * (1 - items['percent_mr_pen']) - items['flat_mr_pen']
        magic_damage_taken = ap_damage * 100 / (100 + mr)
        
        total_damage = total_damage + physical_damage_taken + magic_damage_taken
        
    
    
    return total_damage 


example_abilities_1 = ['Q2', 'W2', 'E2', 'R1', 'E1Q1', 'W1A', 'W1A', 'W1A']

example_abilities_1_1 = ['Q2', 'W2', 'E2', 'R1', 'E1Q1', 'W1A', 'W1A', 'W1A', 'W1A']

example_abilities_2 = ['E1Q1']

# Target stats
health = 3000  # Fixed health value
armor_range = np.linspace(30, 200, 100)
mr = 70  # Fixed magic resist value

'''
# Define target stat ranges
health_range = np.linspace(1500, 4000, 100)
armor_range = np.linspace(30, 200, 10)
mr_range = np.linspace(30, 200, 10)

X, Y = np.meshgrid(armor_range, health_range)
Z_ItemSet1 = np.zeros_like(X)
Z_ItemSet2 = np.zeros_like(X)


for i, health in enumerate(health_range):
    for j, armor in enumerate(armor_range):
        Z_ItemSet1[i, j] = calculate_damage(example_abilities_1, item_sets_13['Item Set 1'], health, armor, mr)
        Z_ItemSet2[i, j] = calculate_damage(example_abilities_1, item_sets_13['Item Set 2'], health, armor, mr)
# Plot the results
fig = plt.figure(figsize=(12, 6))


# Plot for Item Set 1
ax1 = fig.add_subplot(121, projection='3d')
ax1.plot_surface(X, Y, Z_ItemSet1, cmap='viridis')
ax1.set_title('Total Damage with Item Set 1')
ax1.set_xlabel('Armor')
ax1.set_ylabel('Health')
ax1.set_zlabel('Total Damage')

# Plot for Item Set 2
ax2 = fig.add_subplot(122, projection='3d')
ax2.plot_surface(X, Y, Z_ItemSet2, cmap='plasma')
ax2.set_title('Total Damage with Item Set 2')
ax2.set_xlabel('Armor')
ax2.set_ylabel('Health')
ax2.set_zlabel('Total Damage')

plt.tight_layout()
plt.show()

'''

# Calculate damage for each item set across armor values
damage_item_set_1 = [calculate_damage(example_abilities_1, item_sets_13['Item Set 1'], health, armor, mr) for armor in armor_range]
damage_item_set_2 = [calculate_damage(example_abilities_1_1, item_sets_13['Item Set 2'], health, armor, mr) for armor in armor_range]


# Calculate damage differential
damage_differential = np.array(damage_item_set_1) - np.array(damage_item_set_2)

# Plot the results
plt.figure(figsize=(10, 6))
plt.plot(armor_range, damage_differential, label='Damage Differential Serylda - LDR')
plt.xlabel('Armor')
plt.ylabel('Damage Differential')
plt.title('Damage Differential Between Three Item Jayce Lv 13 Serylda vs LDR on 3K HP 70 MR Target Combo 1')
plt.legend()
plt.grid(True)
plt.show()

# Calculate damage for each item set across armor values
damage_item_set_3 = [calculate_damage(example_abilities_2, item_sets_13['Item Set 1'], health, armor, mr) for armor in armor_range]
damage_item_set_4 = [calculate_damage(example_abilities_2, item_sets_13['Item Set 2'], health, armor, mr) for armor in armor_range]


# Calculate damage differential
damage_differential2 = np.array(damage_item_set_3) - np.array(damage_item_set_4)

# Plot the results
plt.figure(figsize=(10, 6))
plt.plot(armor_range, damage_differential2, label='Damage Differential Serylda - LDR')
plt.xlabel('Armor')
plt.ylabel('Damage Differential')
plt.title('Damage Differential Between Three Item Jayce Lv 13 Serylda vs LDR on 3K HP 70 MR Target Combo 2')
plt.legend()
plt.grid(True)
plt.show()


# next plot line graph difference