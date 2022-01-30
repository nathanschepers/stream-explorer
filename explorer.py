import sys

from asciimatics.event import KeyboardEvent, Event
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication
from asciimatics.widgets import (
    Frame,
    Layout,
    Text,
)

from mpv_util import MPVWrapper
from mpv_util.stream_player import StreamPlayer

# to be replaced with... something. wrote to radio.garden about API docs.
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


class PlayerView(Frame):
    __empty_data = {
        "station_location": "-",
        "station_name": "-",
        "artist": "-",
        "song": "-",
        "album": "-",
    }

    def __init__(self, screen: Screen):
        super(PlayerView, self).__init__(
            screen,
            5,
            screen.width,
            on_load=self._load,
            hover_focus=True,
            can_scroll=False,
            title="Player",
        )

        self._player = StreamPlayer(MPVWrapper(), stations_db)
        self._player.register_songinfo_callback(self._update_song)
        self._player.register_stationinfo_callback(self._update_station)

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
        self.data = self.__empty_data
        self.save()
        self._player.force_update()

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

    def process_event(self, event: Event):
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


def player(screen: Screen):
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
