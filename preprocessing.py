import json
import pandas as pd

# --- Boilerplate Code Start ---

# Load the JSON data from the 'text' key
with open('data.json', 'r') as f:
    data = json.load(f)

script = data['text']

# List to hold the categorized data
processed_data = []

# Define categories to filter narrative context from dialogue
CONTEXT_KEYS = ['LOCATION', 'ACTION', 'CHOICE']

for entry in script:
    if not entry: # Safety check for empty dictionaries
        continue
    
    # Get the key and value for the single item in the dictionary
    key = list(entry.keys())[0]
    value = entry[key]
    
    if key in CONTEXT_KEYS:
        # It's a context entry
        processed_data.append({
            'Type': key,
            'Content': value,
            'Speaker': None,
            'Dialogue': None
        })
    else:
        # It's a dialogue entry (Speaker is the key)
        processed_data.append({
            'Type': 'DIALOGUE',
            'Content': None,
            'Speaker': key,
            'Dialogue': value
        })

# Create the final structured DataFrame
df_processed = pd.DataFrame(processed_data)

# --- Boilerplate Code End ---

# The resulting DataFrame (df_processed) now looks like this:
# | Type | Content | Speaker | Dialogue |
# |:---|:---|:---|:---|
# | LOCATION | Sector 1 - The No. 1 Reactor | | |
# | ACTION | The opening sequence: ... | | |
# | DIALOGUE | | Barret | C'mon newcomer. Follow me. |
# | ACTION | Barret runs ahead. ... | | |