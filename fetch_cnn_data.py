#!/usr/bin/env python3

import ujson as json
import requests
import time
import sqlite3
import logging
logging.basicConfig(level=logging.INFO)


def create_sqlite_db(db_name="election_data"):
    '''Create a sqlite DB for election data'''

    conn = sqlite3.connect(f"{db_name}.db",timeout=60.0)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS county (id INTEGER PRIMARY KEY, election_year INT, retrieved_utc INTEGER, state TEXT, data TEXT)')
    c.execute('PRAGMA journal_mode = wal')
    return conn


def fetch_state_abbreviations():
    '''Fetch all US state abbreviations and return dict'''

    url = "https://worldpopulationreview.com/static/states/abbr-name.json"
    r = requests.get(url)
    if r.ok:
        return r.json()


def fetch_county_level_data(state_abbr=None):
    '''Fetch JSON data for counties in a specific state using the state's abbreviation'''

    state_abbr = state_abbr.upper()
    url = f"https://politics-elex-results.data.api.cnn.io/results/view/2020-county-races-PG-{state_abbr}.json"
    r = requests.get(url)
    if r.ok:
        return r.json()


# Create sqlite DB
conn = create_sqlite_db(db_name="election_data")
c = conn.cursor()

state_abbrs_data = fetch_state_abbreviations()
state_abbrs = list(state_abbrs_data.keys())
state_election_data = {}

# Loop through each state and add the state level election data to state_election_data dict
# using the state's abbreviation as the key for that state's data

for state_abbr in state_abbrs:
    state_election_data[state_abbr] = fetch_county_level_data(state_abbr=state_abbr)
    retrieved_utc = int(time.time())
    for county in state_election_data[state_abbr]:
        county_fips_code = county['countyFipsCode']
        state = county['stateAbbreviation'].upper()
        json_data = json.dumps(county, escape_forward_slashes=False, ensure_ascii=False)
        c.execute("INSERT OR IGNORE INTO county (id, retrieved_utc, election_year, state, data) VALUES (?,?,?,?,?)", (county_fips_code, retrieved_utc, 2020, state, json_data))
    conn.commit()
    logging.info(f"Fetched data for {state_abbrs_data[state_abbr]}")
    time.sleep(1)


