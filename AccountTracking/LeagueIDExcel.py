import json
import pandas as pd

# Load the JSON data from file
with open('data_lcs.json', 'r') as file:
    data = json.load(file)

# Convert the JSON data to a DataFrame
df = pd.DataFrame(list(data.items()), columns=['Puuid', 'InGameName'])

# Save the DataFrame to an Excel file
df.to_excel('league_accounts.xlsx', index=False)

print("Data has been written to league_accounts.xlsx")
