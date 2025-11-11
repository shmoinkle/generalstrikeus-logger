# generalstrikeus-signups
A tool to collect, store, and publish up‑to‑date graphs of total signups for the generalstrikeus movement.

## Usage
```
./main.py --help
usage: main.py [-h] [-f | -g SAMPLES OUTPUT_FILE | -r TS_START TS_END MARKERS OUTPUT_FILE]

Fetch and graph the total signatures

options:
  -h, --help            show this help message and exit
  -f, --fetch           Fetch signature total and add to Redis
  -g SAMPLES OUTPUT_FILE, --graph SAMPLES OUTPUT_FILE
                        Generate graph from signature data in Redis.
  -r TS_START TS_END MARKERS OUTPUT_FILE, --raw-graph TS_START TS_END MARKERS OUTPUT_FILE
                        TS_* are raw timestamps in milliseconds.
                        MARKERS is the number of annotated points (0-10)
```

## Setup API
This document explains how to setup authentication for Google Sheets

https://docs.gspread.org/en/latest/oauth2.html

_TL;DR use an **API_KEY** if you're accessing a public document,and a
**SERVICE_ACCOUNT_FILE** if you need granular access_

## Setup & Running
```
## Initial setup ##
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
## Export necessary environment variables

## Run after starting redis ##
source venv/bin/activate
./main.py --fetch
```

## Requirements
- Python
- Redis w/ RedisTimeSeries module

## Todo
- Dockerize
- Simple wiki with common setup and usage