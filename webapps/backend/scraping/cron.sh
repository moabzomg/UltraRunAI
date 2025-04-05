#!/bin/bash

# Move into script directory
cd "$(dirname "$0")"

DATA_DIR="../../frontend/public/data"
RAW_RUNNER_ID_DIR="$DATA_DIR/raw_runner_id_data"
RAW_RUNNER_DIR="$DATA_DIR/raw_runner_data"
RAW_RACE_DIR="$DATA_DIR/raw_race_data"
LOG_DIR="./logs"

mkdir -p "$RAW_RUNNER_ID_DIR" "$RAW_RUNNER_DIR" "$RAW_RACE_DIR" "$LOG_DIR"

# Copy cleaned files into raw_ folders
cp -p "$DATA_DIR/cleaned_runner_id.json" "$RAW_RUNNER_ID_DIR/"
cp -p "$DATA_DIR/cleaned_runner.json" "$RAW_RUNNER_DIR/"
cp -p "$DATA_DIR/cleaned_race.json" "$RAW_RACE_DIR/"

# Run clean.py (expects it to clean and overwrite cleaned_*.json)
python3 clean.py >> "$LOG_DIR/clean.log" 2>&1

# Remove raw data copies to save disk
rm -f "$RAW_RUNNER_ID_DIR"/* "$RAW_RUNNER_DIR"/* "$RAW_RACE_DIR"/*