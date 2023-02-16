import csv
import json
import dxcam
import requests
from threading import Thread
from datetime import datetime, timedelta
from pynput import keyboard, mouse

from functions import get_active_player_name, get_player_champion, is_game_live, get_base_dir, parse_time, format_time
from urls import lol_live_game_stats_url
from overlay import Overlay
from trayicon import TrayIcon
from camera import get_player_cs, region


if __name__ == '__main__':
    base_dir = get_base_dir()
    clears_file = str(base_dir / 'clears.csv')

    with open(clears_file) as csv_file:
        reader = csv.reader(csv_file)
        clears = {(row[2], row[3]): row[6:] for row in reader}
        del clears[('champion', 'start')]
        for clear, times in clears.items():
            clears[clear] = [parse_time(time) for time in times]

    overlay = Overlay()
    camera = dxcam.create(output_color='RGBA')

    class Start:
        def __init__(self):
            self.color = 'blue'

    start = Start()
    start_time = None
    count_time = True
    camp_info = ''

    def input_thread():
        def on_press(key):
            global start_time
            global count_time
            global camp_info

            keys = ['q', 'w', 'e', 'r', 'd', 'f']
            try:
                if str(key) == 'Key.backspace':
                    count_time = not count_time
                    camp_info = ''
                elif key.char in keys:
                    if not count_time:
                        start_time = datetime.now() - timedelta(seconds=90)
                        count_time = True
            except AttributeError:
                '''Special keys such as Backspace'''

        def on_click(x, y, button, pressed):
            global start_time
            global count_time
            if pressed:
                if not count_time:
                    start_time = datetime.now() - timedelta(seconds=90)
                    count_time = True

        listener_keyboard = keyboard.Listener(
            on_press=on_press)
        listener_keyboard.start()

        listener_mouse = mouse.Listener(
            on_click=on_click)
        listener_mouse.start()

    def message_thread():
        global start_time
        global count_time
        global camp_info
        global camera

        while True:
            if is_game_live() and not start_time:
                response = requests.get(lol_live_game_stats_url, verify=False)
                game_time = timedelta(seconds=json.loads(response.text)['gameTime'])
                start_time = datetime.now() + timedelta(seconds=1) - game_time
                # print(start_time)

                champion = get_player_champion(get_active_player_name()).lower()

                overlay.deiconify()
            elif is_game_live() and start_time:

                clear = clears[(champion, start.color)] if (champion, start.color) in clears else None

                if count_time:
                    current_time = format_time(datetime.now() - start_time)

                    cs = get_player_cs(camera, region)
                    if cs != 777:
                        n = 0
                        while cs - 4 >= 0:
                            cs -= 4
                            n += 1
                        if clear and n < 6:
                            if clear[n] > datetime.now() - start_time:
                                time_left = '-' + format_time(clear[n] - (datetime.now() - start_time))
                            else:
                                time_left = '+' + format_time((datetime.now() - start_time) - clear[n])

                            camp_info = f'\nCamp {n + 1}\n{format_time(clear[n])}\n{time_left}'
                        else:
                            camp_info = ''

                    current_time += camp_info
                    overlay.set_message(current_time)
                else:
                    overlay.set_message('Waiting for input...')
            else:
                start_time = None
                # overlay.set_message('Waiting for game...')
                overlay.withdraw()
                # print('Waiting for game...', end='\r')

    tray_thread = Thread(target=lambda: TrayIcon(overlay, start))
    tray_thread.start()

    thread = Thread(target=message_thread)
    thread.start()

    key_thread = Thread(target=input_thread)
    key_thread.start()

    overlay.set_message('Zilean\nSTARTING\nIt will minimize to system tray')
    overlay.run()
