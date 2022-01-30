from collections.abc import Callable
import sys

from asciimatics.event import KeyboardEvent
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication
from asciimatics.widgets import (
    Frame,
    Layout,
    Text,
)

import mpv_util

# to be replaced with... something
stations_db = [
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


class Player:
    def __init__(self, player, stations):
        self._mpv_player = player
        self._playing = False
        self._stations = stations
        self._station_index = 0
        self._songinfo_callback = lambda _: None
        self._stationinfo_callback = lambda _: None
        mpv_util.register_title_callback(self._update_songinfo)

    def register_songinfo_callback(self, callback: Callable) -> None:
        self._songinfo_callback = callback

    def register_stationinfo_callback(self, callback: Callable) -> None:
        self._stationinfo_callback = callback

    def initialize(self):
        self._update_stationinfo()

    def _update_songinfo(self, songinfo: str) -> None:
        if (
                songinfo
                and songinfo not in self._stations[self._station_index]["title_ignore"]
        ):
            (artist, song, *album) = self._stations[self._station_index][
                "title_parser"
            ](songinfo)
            details = {
                "artist": artist,
                "song": song,
                "album": "-".join(str(n) for n in album),
            }
        else:
            details = {
                "artist": "-",
                "song": "-",
                "album": "-",
            }
        self._songinfo_callback(details)

    def _update_stationinfo(self) -> None:
        self._stationinfo_callback(self.current_station)

    @property
    def current_station(self) -> dict[str, str]:
        return {
            "station_location": self._stations[self._station_index]["country"],
            "station_name": self._stations[self._station_index]["name"],
        }

    def play(self) -> None:
        self._mpv_player.play(self._stations[self._station_index]["stream"])
        self._playing = True

    def pause(self) -> None:
        self._mpv_player.stop()
        self._playing = False

    def play_pause(self) -> None:
        self.play() if not self._playing else self.pause()

    def next_station(self) -> None:
        self._station_index = (self._station_index + 1) % len(self._stations)
        self._update_stationinfo()
        self.play()

    def previous_station(self) -> None:
        self._station_index = (self._station_index - 1) % len(self._stations)
        self._update_stationinfo()
        self.play()


class PlayerView(Frame):
    empty_data = {
        "station_location": "-",
        "station_name": "-",
        "artist": "-",
        "song": "-",
        "album": "-",
    }

    def __init__(self, screen):
        super(PlayerView, self).__init__(
            screen,
            5,
            screen.width,
            on_load=self._load,
            hover_focus=True,
            can_scroll=False,
            title="Player",
        )

        self._player = Player(mpv_util.mpv_player, stations_db)
        self._player.register_songinfo_callback(self._update_song)
        self._player.register_stationinfo_callback(self._update_station)
        self._player.initialize()

        # Label initialization (station)
        self._station_location = Text(
            label="Location:",
            name="station_location",
            disabled=True,
        )
        self._station_name = Text(
            label="Name:",
            name="station_name",
            disabled=True,
        )

        # Label initialization (song)
        self._artist = Text(label="Artist:", name="artist", disabled=True)
        self._song = Text(label="Song:", name="song", disabled=True)
        self._album = Text(label="Album:", name="album", disabled=True)

        # set up layout and widgets
        layout = Layout([25, 25, 50], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._station_location, 0)
        layout.add_widget(self._station_name, 0)
        layout.add_widget(self._artist, 1)
        layout.add_widget(self._song, 1)
        layout.add_widget(self._album, 1)
        self.fix()

    def _load(self):
        self.data = self.empty_data
        self.save()

    def _update_song(self, song_details: dict[str, str]) -> None:
        """this is called from the player when new song information is available"""
        self.data = song_details
        self.save()
        self.screen.force_update()

    def _update_station(self, station_details: dict[str, str]) -> None:
        """this is called from the player when new station information is available"""
        self.data = station_details
        self.save()
        self.screen.force_update()

    def play_pause(self):
        self._player.play_pause()

    def previous_station(self):
        self._player.previous_station()

    def next_station(self):
        self._player.next_station()

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            c = event.key_code

            match c:
                case 100:
                    print(str(self.data) + "\r")
                case 104:
                    self.previous_station()
                case 108:
                    self.next_station()
                case 112:
                    self.play_pause()
                case (3 | 113):
                    raise StopApplication("User terminated app")


def player(screen):
    scenes = [
        Scene([PlayerView(screen)], -1, name="Station Explorer"),
    ]

    screen.play(
        scenes,
        stop_on_resize=True,
        start_scene=scenes[0],
        allow_int=True,
    )


while True:
    try:
        Screen.wrapper(player, catch_interrupt=True)
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene
