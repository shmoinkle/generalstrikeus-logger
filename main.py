#!/usr/bin/env python3
import os
import sys
import argparse
import gspread
from redis import Redis
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

"""
Gets integer of single cell in a Google Sheet and stores it as in a RedisTimeSeries key.

Required environment variables:
	SERVICE_ACCOUNT_FILE	- Path to service account JSON file OR:
	API_KEY					- Google API Key (Grab from Google Cloud Console)
	SHEET_ID				- Google Sheet ID (Grab from its URL)

Optional environment variables:
	SHEET					- Worksheet index (default: 0)
	CELL					- Cell to read (default: "A2")
	REDIS_URL				- Redis connection URL (default: "redis://localhost:6379/0")
	REDIS_TS_KEY			- RedisTimeSeries key to store the va (default: "total")
"""

SERVICE_ACCOUNT_FILE = os.environ.get("SERVICE_ACCOUNT_FILE")
API_KEY = os.environ.get("API_KEY")
SHEET_ID = os.environ.get("SHEET_ID")
SHEET = os.environ.get("SHEET", 0)
CELL = os.environ.get("CELL", "A2")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
REDIS_TS_KEY = os.environ.get("REDIS_TS_KEY", "total")

def get_ts():
	'''
	Return current timestamp in milliseconds.
	'''
	return int(datetime.now().timestamp() * 1000)

def check_type(input):
	'''
	Check argument type and convert to int if possible
	'''
	try:
		return int(input)
	except ValueError:
		return input

def service_account(service_account_file):
	'''
	Return gspread client authenticated with service account file.
	'''
	return gspread.service_account(filename=service_account_file,scopes=gspread.auth.READONLY_SCOPES)

def api(api_key):
	'''
	Return gspread client authenticated with API key.
	'''
	return gspread.api_key(api_key)

def get_value(gc, sheet_id, sheet, cell):
	'''
	Return the current value of Google Sheet cell.
	Assumes the cell contains a numeric value and returns None otherwise.
	'''
	value = gc.open_by_key(sheet_id).get_worksheet(sheet).acell(cell).numeric_value
	ts = get_ts()
	return value, ts

def add_value(conn, key, ts, value):
	'''
	Add value to RedisTimeSeries key.
	'''
	conn.ts().add(key, ts, value, retention_msecs=0)

def generate_graph(conn, key, samples, output_file):
	'''
	Generate a line graph from the collected totals in Redis.
	Saves the plot to `output_file`.
	'''
	# fetch most recent samples (count limits number of points returned)
	points = conn.ts().range(key, '-', '+', count=samples)
	if not points:
		print(f"No data for key {key}", file=sys.stderr)
		return
	timestamps = [datetime.fromtimestamp(int(ts) / 1000) for ts, _ in points]
	values = [float(val) for _, val in points]

	plt.figure(figsize=(10, 4))
	plt.plot(timestamps, values, marker='o', linestyle='-')
	plt.xlabel("Time")
	plt.ylabel("Total Signatures")
	plt.title(f"Total Signatures Over Time")
	plt.grid(True)
	plt.tight_layout()
	plt.savefig(output_file)
	plt.close()
	print(f"Saved plot to {output_file}")

def parse_args():
	parser = argparse.ArgumentParser(description="Fetch and graph the total signatures")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-f", "--fetch", action="store_true", help="Fetch signature total and add to Redis")
	group.add_argument("-g", "--graph", type=check_type, nargs=2, metavar=("SAMPLES", "OUTPUT_FILE"),
					help="Generate graph from signature data in Redis.")
	return parser.parse_args()

def main():
	args = parse_args()
	r = Redis.from_url(REDIS_URL, decode_responses=True)
	if args.fetch:
		if not (SERVICE_ACCOUNT_FILE or API_KEY) or not SHEET_ID:
			print("Missing SERVICE_ACCOUNT_FILE/API_KEY or SHEET_ID environment variable", file=sys.stderr)
			sys.exit(1)
		if API_KEY:
			gc = api(API_KEY)
		else:
			gc = service_account(SERVICE_ACCOUNT_FILE)
		total, ts = get_value(gc, SHEET_ID, SHEET, CELL)
		if not isinstance(total, int):
			print(f"Cell {CELL} is not numeric", file=sys.stderr)
			sys.exit(1)
		add_value(r, REDIS_TS_KEY, ts, total)
		print(f"Stored {total} into {REDIS_TS_KEY}")

	if args.graph:
		if not isinstance(args.graph[0], int):
			print(f"Number of samples must be an integer", file=sys.stderr)
			sys.exit(1)
		generate_graph(r, REDIS_TS_KEY, args.graph[0], str(args.graph[1]))
if __name__ == "__main__":
	main()