#!/bin/bash

# Define range for race UID
MIN_RACE_UID=1
MAX_RACE_UID=100000
STEP=5000

# Loop through the range and run race_scraper.py in batches
for ((start=$MIN_RACE_UID; start<=$MAX_RACE_UID; start+=$STEP))
do
    end=$((start + STEP - 1))
    if [ $end -gt $MAX_RACE_UID ]; then
        end=$MAX_RACE_UID
    fi
    echo "Running race scraper from UID $start to $end..."
    python3 race_scraper.py --min_race_uid $start --max_race_uid $end --year_start 2003 --year_end 2025
done