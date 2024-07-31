import requests
import time
import pandas as pd
import json


API_KEY = "RGAPI-b710008a-d14a-46f9-9399-273ad534e7ec"
REGION = "americas"

# My puuid, gamename, tagline
myPuuid =  "RGjbd24ZaxizENVpxVM3Uran5JULKnNWrfvjQVDuz92tEbpItaslEu_ualtlTq4yI6hhSSjKhp2pqg",
myGameName = "RoseThorn",
myTagLine = "Rose"


# List of in-game names (including taglines)
summoner_names = [
    "RoseThorn#Rose",
    "whitespace#srtty"
    # Add more names as needed
]

names_100 = ["100 Sniper#NA1",
             "100 Batman#123",
             "THE INTING GUY#int",
             "tree frog#100",
             "tiki and taka#NA1",
             "Yves#100",
             "Happy Game#NA2",
             "ae3aaq34e5yh#NA1",
             "Tomo#0999" #tomo
             "idontcare#NA3",
             "White#EX1"
]

names_C9 = ["God of death#kr2",
            "F9 Cudge#NA1",
            "blaberfish2#NA1",
            "jjjjjjjjj#1212",
            "C9C9C9C9C9#NA1",
            "C9 Berserker#NA1",
            "xczasdqwedfh1dv#2336",
            "VULCAN#5125"]

# Jensen acc ASCII case
names_DIG = ["I choose to play#enjoy",
             "Licorice#NA1",
             "ASTROBOY99#NA1",
             "Spica#001",
             "stayawayz#NA1",
             "Jænsen#NA1",
             "Zven#KEKW1",
             "galbiking#000",
             "Isles1#NA1"
]

names_FLY = ["I will trade#NA1",
             "Andrew Barton#FLYGM",
             "FLY Quad#123",
             "KaiGyt#0187",
             "FLY Busio#000",   
             "Andrew Barter#1600"
             

]

names_IMT = ["Castle#jo13",
             "ARMAO#NA1",
             "Being left#owo",
             "Tactical0#NA1",
             "Olleh#IMT",
             "Wekin Poof#NA1"
    
]

names_NRG = ["Dhokla#NA1",
             "appleorange#peach",
             "tupo#tupo",
             "Palafoxy#CHOMP",
             "ADCADC123#NA1",
             "huhi#0246",
             "NINERS#3333"

]

# bvoy acc doesnt work, special char
names_SR = ["faker god top#NA1",
            "My Dream LCS#NA1",
            "T0mio#NA1",
            "c2 meteos#NA1",
            "giga smoker#420",
            "Bvoy#SRSR",
            #"ώώώώ#0106",
            "Cosboat#NA1",
            "CCJT#NA1",
            "big bush#69420",
            "oval#2768",
            "2wfrevdxsc#NA1",
            "Zeyzal#NA2"
]

names_TL = ["TL HONDA IMPACT#XDDD",
            "TL Honda UmTi#0602",
             "JKBT UmTi#0602",
            "yaptain#usa",
            "lcs villain#APA",
            "TL Honda Yeon#NA1",
            "SCALING PLAYER#TL7",
            "TL Honda CoreJJ#1123",
             
]

# URL template to get summoner information by ign
SUMMONER_URL = f'https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{{}}/{{}}?api_key={API_KEY}'


# get puuid using the summoner ign
def get_summoner_puuid(summoner_name):

    #     RoseThorn#Rose

    # split summoner name into gamename and tagline
    gameName = summoner_name.split('#')[0]
    tagLine = summoner_name.split('#')[1]

    # format URL 
    url = SUMMONER_URL.format(gameName, tagLine)
    
    # request from riot api
    response = requests.get(url)

    # valid summoner ign found
    if response.status_code == 200:
        return response.json().get('puuid')

    else:
        print(f"Error {response.status_code}: Unable to retrieve data for {summoner_name}")
        return None
    

# Dictionary to store summoner IDs and names
summoner_data = {}

# Loop through each summoner name and retrieve their ID
for name in names_100:
    summoner_id = get_summoner_puuid(name)
    if summoner_id:
        summoner_data[name] = summoner_id
    time.sleep(1.2)  # Rate limiting: 50 requests per 1 second

# Loop through each summoner name and retrieve their ID
for name in names_C9:
    summoner_id = get_summoner_puuid(name)
    if summoner_id:
        summoner_data[name] = summoner_id
    time.sleep(1.2)  # Rate limiting: 50 requests per 1 second

for name in names_FLY:
    summoner_id = get_summoner_puuid(name)
    if summoner_id:
        summoner_data[name] = summoner_id
    time.sleep(1.2)  # Rate limiting: 50 requests per 1 second

for name in names_DIG:
    summoner_id = get_summoner_puuid(name)
    if summoner_id:
        summoner_data[name] = summoner_id
    time.sleep(1.2)  # Rate limiting: 50 requests per 1 second
for name in names_IMT:
    summoner_id = get_summoner_puuid(name)
    if summoner_id:
        summoner_data[name] = summoner_id
    time.sleep(1.2)  # Rate limiting: 50 requests per 1 second

for name in names_NRG:
    summoner_id = get_summoner_puuid(name)
    if summoner_id:
        summoner_data[name] = summoner_id
    time.sleep(1.2)  # Rate limiting: 50 requests per 1 second

for name in names_SR:
    summoner_id = get_summoner_puuid(name)
    if summoner_id:
        summoner_data[name] = summoner_id
    time.sleep(1.2)  # Rate limiting: 50 requests per 1 second

for name in names_TL:
    summoner_id = get_summoner_puuid(name)
    if summoner_id:
        summoner_data[name] = summoner_id
    time.sleep(1.2)  # Rate limiting: 50 requests per 1 second

# Print the results
for name, summoner_id in summoner_data.items():
    print(f"Summoner Name: {name}, Summoner ID: {summoner_id}")


# Optionally, save the data to a file for future reference
with open('data_lcs.json', 'w') as f:
    json.dump(summoner_data, f, indent=4)




summoner_puuids = ["RGjbd24ZaxizENVpxVM3Uran5JULKnNWrfvjQVDuz92tEbpItaslEu_ualtlTq4yI6hhSSjKhp2pqg",
                    "H0vgUX-f5tet5-Q3tL_LrJ7X7eQiZFiwTngYtBu80XYl38MmNwTWIV5X7DltO6X_qYR7B_YHucGYGQ"
                    # Add more names as needed
                    ]

SUMMONER_URL2 = f'https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{{}}?api_key={API_KEY}'

def get_summoner_ign(puuid):
    gameName = ""
    tagLine = ""

    # format URL 
    url = SUMMONER_URL2.format(puuid)

    # request from riot api
    response = requests.get(url)

    # valid summoner ign found
    if response.status_code == 200:
        gameName = response.json().get('gameName')
        tagLine = response.json().get('tagLine')
        ign = gameName + "#"+ tagLine
        return ign


    else:
        print(f"Error {response.status_code}: Unable to retrieve data for {puuid}")
        return None

# Dictionary to store summoner IDs and names
summoner_data2 = {}   


# Loop through each summoner name and retrieve their ID
for puuid in summoner_puuids:
    ign = get_summoner_ign(puuid)
    if ign:
        summoner_data2[puuid] = ign
    time.sleep(1.2)  # Rate limiting: 50 requests per 1 second

# Print the results
for summoner_id, name in summoner_data2.items():
    print(f"Summoner Name: {name}, Summoner ID: {summoner_id}")


myURL = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/RGjbd24ZaxizENVpxVM3Uran5JULKnNWrfvjQVDuz92tEbpItaslEu_ualtlTq4yI6hhSSjKhp2pqg?api_key=RGAPI-5cc10fc2-1d6b-4979-9538-6ff66ae4026a"




with open('summoner_data2.json', 'w') as f:
    json.dump(summoner_data2, f, indent=4)





