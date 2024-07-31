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

# Dictionary to store summoner IDs and names
summoner_data2 = {}   

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






myURL = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/RGjbd24ZaxizENVpxVM3Uran5JULKnNWrfvjQVDuz92tEbpItaslEu_ualtlTq4yI6hhSSjKhp2pqg?api_key=RGAPI-5cc10fc2-1d6b-4979-9538-6ff66ae4026a"




# Function to recursively get all values from a JSON object
def get_all_values(obj):
    if isinstance(obj, dict):
        for value in obj.values():
            yield from get_all_values(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from get_all_values(item)
    else:
        yield obj

# Read the JSON file
with open('data_lcs.json', 'r') as file:
    data = json.load(file)

# Get all values
all_values = list(get_all_values(data))

# Print all values
for value in all_values:
    ign = get_summoner_ign(value)
    if ign:
        summoner_data2[value] = ign
    time.sleep(1.2)  # Rate limiting: 50 requests per 1 second

# Print the results
for summoner_id, name in summoner_data2.items():
    print(f"Summoner Name: {name}, Summoner ID: {summoner_id}")



with open('data_lcs2.json', 'w') as f:
    json.dump(summoner_data2, f, indent=4)