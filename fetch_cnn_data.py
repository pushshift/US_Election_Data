#!/usr/bin/env python3

import ujson as json
import requests
import time


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



state_abbrs_data = fetch_state_abbreviations()
state_abbrs = list(state_abbrs_data.keys())
state_election_data = {}

# Loop through each state and add the state level election data to state_election_data dict
# using the state's abbreviation as the key for that state's data

for state_abbr in state_abbrs:
    state_election_data[state_abbr] = fetch_county_level_data(state_abbr=state_abbr)
    print(state_election_data)
    time.sleep(1)


