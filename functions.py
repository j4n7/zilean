import sys
import json
import urllib3
import requests

from pathlib import Path
from datetime import datetime, timedelta

from urls import (lol_live_game_stats_url, lol_live_game_events_url,
                  lol_live_player_name_url, lol_live_players_url)


# Disable insecure https warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.adapters.DEFAULT_RETRIES = 5


def get_game_events():
    response = requests.get(lol_live_game_events_url, verify=False)
    events = json.loads(response.text)['Events']
    return events


def get_player_list():
    response = requests.get(lol_live_players_url, verify=False)
    players = json.loads(response.text)
    return players


def get_active_player_name():
    response = requests.get(lol_live_player_name_url, verify=False)
    name = json.loads(response.text).split('#')[0]
    return name


def get_player_champion(name):
    for player in get_player_list():
        if player['summonerName'] == name:
            active_player = player
            break
    active_player_champion = active_player['championName']
    return active_player_champion


def is_game_live():
    game_started = False
    try:
        response = requests.get(lol_live_game_stats_url, verify=False)
        status_code = response.status_code
        if status_code == 200:
            events = get_game_events()
            game_started = True if events and 'GameStart' in [event['EventName'] for event in events] else False
    except requests.exceptions.ConnectionError:
        pass
    return game_started


def get_base_dir():
    '''Get absolute path to base directory, works for dev and for PyInstaller'''
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_dir = Path(sys._MEIPASS)
    else:
        base_dir = Path(__file__).parent
    return base_dir


def parse_time(time):
    time = datetime.strptime(time, '%M:%S')
    delta = timedelta(minutes=time.minute, seconds=time.second)
    return delta


def format_time(delta):
    min, sec = divmod(delta.seconds, 60)
    return '%02d:%02d' % (min, sec)
