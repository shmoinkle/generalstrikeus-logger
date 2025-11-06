#!/usr/bin/env bash

# This script populates the dev database with fake data for testing graph generation

# Clear existing data
redis-cli DEL dev

# We set the initial timestamp to midnight today, in milliseconds
TS=$(( $(date -d "$(date +%F) 00:00:00" +%s) * 1000 ))

# Start between 400,000 and 401,000 signatures
SIGNATURES=$((400000 + RANDOM % 1001))

# Run 1440 times to simulate 1 day of data
for RUN in $(seq 1 1440); do
    # Increase 0-5 randomly (oooo very generous)
    INC=$((RANDOM % 6))
    SIGNATURES=$((SIGNATURES + INC))
    # We add the equivalent of 1 minute in milliseconds each loop
    TS=$((TS += 60000))
    # Add the fake data point while echoing the command for visibility
    set -x
    redis-cli TS.ADD dev $TS $SIGNATURES
    set +x
done