
import json
import os
import glob
import shutil


DATA_DIR = "../../frontend/public/data/"
RACE_JSON_DIR = os.path.join(DATA_DIR, "raw_race/")
RUNNER_JSON_DIR = os.path.join(DATA_DIR, "raw_runner/")
RUNNER_ID_JSON_DIR = os.path.join(DATA_DIR, "raw_runner_id/")
CLEANED_RACE_JSON_PATH = os.path.join(DATA_DIR, "cleaned_race.json")
CLEANED_RUNNER_JSON_PATH = os.path.join(DATA_DIR, "cleaned_runner.json")
CLEANED_RUNNER_ID_JSON_PATH = os.path.join(DATA_DIR, "cleaned_runner_id.json")


def load_json_from_directory(directory_path,initialise):
    all_data = initialise
    # Iterate over each file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r") as file:
                try: 
                    data = json.load(file)
                    if type(initialise) is list: # for runner and runner_id json list
                        all_data.extend(data) 
                    else: # for race json dict
                         all_data.update(data)
                    print(f"json in {file_path} extracted")
                except ValueError as e:
                    print (f"Error in file {file_path}:{e}")
    return all_data


def save_json(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


# --- Clean and Rank RUNNER_JSON ---
runners_data = load_json_from_directory(RUNNER_JSON_DIR,[])

# Remove duplicates, keeping the last occurrence
cleaned_data = {runner["id"]: runner for runner in runners_data}.values()

# Convert UTMB index to integers (handling missing values as 0)
def parse_utmb_index(index):
    return int(index) if index.isdigit() else 0


def total_utmb_score(runner):
    utmb_index = runner.get("UTMB Index", {})
    general = parse_utmb_index(utmb_index.get("General", "0"))
    total_other = sum(parse_utmb_index(utmb_index.get(k, "0")) for k in ["20K", "50K", "100K", "100M"])
    return general, total_other


# Sort by General UTMB Index first, then by total of 20K, 50K, 100K, 100M
sorted_runners = sorted(cleaned_data, key=total_utmb_score, reverse=True)

save_json(CLEANED_RUNNER_JSON_PATH, sorted_runners)
print(f"Ranked and cleaned runner data saved to '{CLEANED_RUNNER_JSON_PATH}'.")


# --- Clean RACE_JSON ---
races_data = load_json_from_directory(RACE_JSON_DIR,{})

# Clean by keeping only the last occurrence of each race ID
cleaned_race_data = {race_id: race_data for race_id, race_data in races_data.items()}

save_json(CLEANED_RACE_JSON_PATH, cleaned_race_data)
print(f"Ranked and cleaned race data saved to '{CLEANED_RACE_JSON_PATH}'.")


# --- Clean and Deduplicate RUNNER_ID_JSON ---
runner_ids_data = load_json_from_directory(RUNNER_ID_JSON_DIR,[])

# Remove duplicates, keeping only the last occurrence of each ID
unique_runner_ids = list(dict.fromkeys(runner_ids_data))

save_json(CLEANED_RUNNER_ID_JSON_PATH, unique_runner_ids)
print(f"Cleaned runner IDs saved to '{CLEANED_RUNNER_ID_JSON_PATH}'.")

        