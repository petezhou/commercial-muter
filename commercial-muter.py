import os
import sys
import time
import requests
import numpy as np
import cv2 as cv
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def send_roku_command(command):
    url = f'http://{ROKU_IP}:8060/keypress/{command}'
    response = requests.post(url)
    if response.status_code != 200:
        print(f"Failed to send Mute/Unmute command. Status code: {response.status_code}")

def pause_spotify(sp):
    try:
        sp.pause_playback(device_id=DEVICE_ID)
    except Exception as e:
        print(f"Pausing Spotify failed. {e}")

def play_spotify(sp):
    try:
        sp.start_playback(device_id=DEVICE_ID)
    except Exception as e:
        print(f"Starting Spotify failed. {e}")

def start_video():
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    return cap


# Start script
VERBOSE_LOG = '-v' in sys.argv
SPOTIFY_ENABLED = '-s' in sys.argv

MATCH_TEMPLATE_PATH = os.environ["MATCH_TEMPLATE_PATH"]
MATCH_THRESHOLD = float(os.environ["MATCH_THRESHOLD"])
MUTE_DELAY = float(os.environ["MUTE_DELAY"])
DEVICE_ID = os.environ["DEVICE_ID"]
ROKU_IP = os.environ["ROKU_IP"]

if SPOTIFY_ENABLED:
    scope = "user-library-read,user-read-playback-state,user-modify-playback-state,user-top-read"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    print(sp.devices())

template = cv.imread(MATCH_TEMPLATE_PATH, cv.IMREAD_GRAYSCALE)
template_height, template_width = template.shape[:2]
cap = start_video()

is_game = True
no_game_count = 0
while True:
    ret, frame = cap.read()
    while not ret:
        print("Cannot receive frame, trying to restart video capture.")
        cap.release()
        cv.destroyAllWindows()
        time.sleep(8)
        cap = start_video()
        ret, frame = cap.read()

    # try to match
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    result = cv.matchTemplate(gray, template, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    # rectangle around match
    top_left = max_loc
    bottom_right = (top_left[0] + template_width, top_left[1] + template_height)
    cv.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

    # status changes
    if max_val > MATCH_THRESHOLD:
        if is_game:
            if no_game_count > 0:
                no_game_count = 0
        else:
            is_game = True
            no_game_count = 0
            print("Starting Game mode.")
            if SPOTIFY_ENABLED:
                pause_spotify(sp)
            send_roku_command('VolumeMute')
    else:
        if VERBOSE_LOG:
            print(f"No match. Rate: {max_val} < {MATCH_THRESHOLD}")

        if is_game:
            if no_game_count > MUTE_DELAY:
                is_game = False
                print(f"Starting Mute mode after {MUTE_DELAY // 10} seconds.")
                if SPOTIFY_ENABLED:
                    play_spotify(sp)
                send_roku_command('VolumeMute')
            else:
                no_game_count += 1

    cv.imshow('frame', frame)

    if cv.waitKey(1) == ord('q'):
        break
 
cap.release()
cv.destroyAllWindows()
