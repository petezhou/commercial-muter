# Commercial Muter

Mutes the TV when the game is in commercial. Optionally play music from Spoitfy when TV is muted.

## Runbook
1) `vim run-commercial-muter.sh`
```
export MATCH_TEMPLATE_PATH=<path/to/screenshot>
export MATCH_THRESHOLD="0.75"
export MUTE_DELAY="300"
export DEVICE_ID="1e567bf4-8144-4576-8559-f8bba7ba2ba0_amzn_1"

export SPOTIPY_CLIENT_ID=<your spotify app id>
export SPOTIPY_CLIENT_SECRET=<your spotify app secret>
export SPOTIPY_REDIRECT_URI="http://localhost:8888/callback/"

python3 commercial-muter.py $1 $2
```
2) Connect a camera and point it at the bottom of your TV
3) `./run-commercial-muter.sh`
4) Take a screenshot of a piece of the scoreboard (team logo)
5) Save the screenshot to /path/to/screenshot (configured in script)
6) Restart the program

#### Options:  
* `-s` play Spotify when TV is muted (you'll need to create a Spotify app in developer mode and authenticate)
* `-v` for verbose logging to help debug OpenCV matching

