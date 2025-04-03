import sys
import os
import json

def split_runner_ids(filepath, interval):
    """Splits the runner_id JSON file into smaller chunks based on the interval."""
    # Load runner IDs from the JSON file
    try:
        with open(filepath, "r") as file:
            runner_ids = json.load(file)
        
        if not isinstance(runner_ids, list):
            raise ValueError("Invalid JSON format: Expected a list of runner IDs.")

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        sys.exit(1)

    total_runners = len(runner_ids)
    if total_runners == 0:
        print("The input JSON file is empty.")
        sys.exit(1)

    print(f"Total runners: {total_runners}, Splitting every {interval} runners.")

    # Create output files
    base_filepath = os.path.abspath(filepath)
    for i, start in enumerate(range(0, total_runners, interval), start=1):
        output_path = f"{base_filepath[:-5]}.{i}.json"
        chunk = runner_ids[start:start + interval]

        with open(output_path, "w") as out_file:
            json.dump(chunk, out_file, indent=4)

        print(f"Created: {output_path} ({len(chunk)} runners)")

    print("Splitting completed successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 split_runner_id.py <filepath to runner_id> <interval>")
        sys.exit(1)

    input_filepath = sys.argv[1]
    try:
        interval = int(sys.argv[2])
        if interval <= 0:
            raise ValueError
    except ValueError:
        print("Error: Interval must be a positive integer.")
        sys.exit(1)

    split_runner_ids(input_filepath, interval)
