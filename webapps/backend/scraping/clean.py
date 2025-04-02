import json
import os

DATA_DIR = "../../frontend/public/data/"
RACE_JSON_PATH = os.path.join(DATA_DIR, "race.json")
RUNNER_JSON_PATH = os.path.join(DATA_DIR, "runner.json")
RUNNER_ID_JSON_PATH = os.path.join(DATA_DIR, "runner_id.json")
CLEANED_RACE_JSON_PATH = os.path.join(DATA_DIR, "cleaned_race.json")
CLEANED_RUNNER_JSON_PATH = os.path.join(DATA_DIR, "cleaned_runner.json")
CLEANED_RUNNER_ID_JSON_PATH = os.path.join(DATA_DIR, "cleaned_runner_id.json")
with open(RACE_JSON_PATH, "r") as file:
    data = json.load(file)
    
cleaned_data = {}
for key, value in data.items():
    cleaned_data[key] = value  # The last occurrence of the key remains

with open(CLEANED_RACE_JSON_PATH, "w") as file:
    json.dump(cleaned_data, file, indent=4)

print(f"Cleaned data saved to '{CLEANED_RACE_JSON_PATH}'.")

with open(RUNNER_JSON_PATH, "r") as file:
    data = json.load(file)
    
cleaned_data = list({runner["id"]: runner for runner in data})

with open(CLEANED_RUNNER_JSON_PATH, "w") as file:
    json.dump(cleaned_data, file, indent=4)

print(f"Cleaned data saved to '{CLEANED_RUNNER_JSON_PATH}'.")

with open(RUNNER_ID_JSON_PATH, "r") as file:
    data = json.load(file)
    
unique_ids = list(dict.fromkeys(data))
with open(CLEANED_RUNNER_ID_JSON_PATH, "w") as file:
    json.dump(cleaned_data, file, indent=4)

print(f"Cleaned data saved to '{CLEANED_RUNNER_ID_JSON_PATH}'.")
