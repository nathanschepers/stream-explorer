#!/usr/bin/env python3
from mpv_util import player, set_title_callback
import readchar

stations = [
    {
        "name": "Radio Thiossane",
        "country": "Senegal",
        "stream": "http://listen.senemultimedia.net:8110/stream",
        "title_ignore": [
            "stream",
            "Advert: - Advert:",
        ],
        "title_parser": lambda s: (s.split(" - ") + [None]),
    },
    {
        "name": "Dr. Dick's Dub Shack",
        "country": "Bermuda",
        "stream": "https://streamer.radio.co/s0635c8b0d/listen",
        "title_ignore": [
            "listen",
            "rob - dub shack intermission",
        ],
        "title_parser": lambda s: (s.split(" - ")),
    },
]


class PlayerActions:
    def __init__(
        self,
    ):
        self.station_index = 0
        self.player = player
        self.now_playing = None
        self.playing = False
        self.new = True
        set_title_callback(self._set_now_playing)

    def _set_now_playing(self, value):
        if value and value not in stations[self.station_index]["title_ignore"]:
            if value == self.now_playing:
                return
            self.now_playing = value
            (artist, song, *album) = stations[self.station_index]["title_parser"](
                self.now_playing
            )
            print(f"  {artist}: {song} - {album}\r")

    def _play_current(self):
        player.play(stations[self.station_index]["stream"])

    def _print_station_details(self):
        name = stations[self.station_index]["name"]
        country = stations[self.station_index]["country"]
        print(f"{self.station_index} - {country} - {name}.")

    def pause(self):
        player.stop()
        self.playing = False

    def play(self, show_station_details=True):
        if show_station_details or self.new:
            self._print_station_details()
        self._play_current()
        self.playing = True
        self.new = False

    def play_pause(self):
        self.pause() if self.playing else self.play(show_station_details=False)

    def previous_station(self):
        self.station_index = (self.station_index - 1) % len(stations)
        self.now_playing = None
        self.play()

    def next_station(self):
        self.station_index = (self.station_index + 1) % len(stations)
        self.now_playing = None
        self.play()


actions = PlayerActions()

action_mappings = {
    "p": actions.play_pause,
    "h": actions.previous_station,
    "l": actions.next_station,
    "q": exit,
}


def main_loop():
    print("...")

    # main ui loop
    while True:
        action = readchar.readchar()
        if action and action in action_mappings:
            action_mappings[action]()


if __name__ == "__main__":
    main_loop()
