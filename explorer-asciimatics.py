from asciimatics.widgets import (
    Frame,
    Layout,
    Label,
    Text,
)
from asciimatics.event import Event, KeyboardEvent
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication
import sys

from mpv_util import player, set_title_callback


class UpdateEvent(Event):
    def __init__(self, song_details):
        super(UpdateEvent, self).__init__()
        self.song_details = song_details


# to be replaced
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


class SomeView(Frame):
    empty_data = {
        "station_location": "-",
        "station_name": "-",
        "artist": "-",
        "song": "-",
        "album": "-",
    }

    def __init__(self, screen, player):
        super(SomeView, self).__init__(
            screen,
            5,
            screen.width,
            on_load=self._load,
            hover_focus=True,
            can_scroll=False,
            title="Player",
        )

        # player initialization
        self._player = player
        self._playing = False
        self._station_index = 0
        set_title_callback(self._update_song)

        # Label initialization (station)
        self._station_location = Text(
            label="Location:",
            # stations[self._station_index]["country"],
            name="station_location",
            disabled=True,
        )
        self._station_name = Text(
            label="Name:",
            # stations[self._station_index]["name"],
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
        # self.screen.force_update()

    def _update_song(self, value):
        station_name = stations[self._station_index]["name"]
        station_country = stations[self._station_index]["country"]

        if value and value not in stations[self._station_index]["title_ignore"]:
            (artist, song, *album) = stations[self._station_index]["title_parser"](
                value
            )

            details = {
                "station_location": station_country,
                "station_name": station_name,
                "artist": artist,
                "song": song,
                "album": "-".join(str(n) for n in album),
            }

            self.data = details
            self.save()
            self.screen.force_update()

        else:
            song_details = {
                "station_location": station_country,
                "station_name": station_name,
                "artist": "-",
                "song": "-",
                "album": "-",
            }

            self.data = song_details
            self.save()
            self.screen.force_update()

    def _update_station(self):
        name = stations[self._station_index]["name"]
        country = stations[self._station_index]["country"]
        station_details = {
            "station_location": country,
            "station_name": name,
            "artist": "-",
            "song": "-",
            "album": "-",
        }
        self.data = station_details
        self.save()

    def _play_current(self):
        player.play(stations[self._station_index]["stream"])

    def pause(self):
        player.stop()
        self._playing = False

    def play(self):
        self._update_station()
        self._play_current()
        self._playing = True

    def play_pause(self):
        self.play() if not self._playing else self.pause()

    def previous_station(self):
        self._station_index = (self._station_index - 1) % len(stations)
        self.play()

    def next_station(self):
        self._station_index = (self._station_index + 1) % len(stations)
        self.play()

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            c = event.key_code

            # previous_station on h
            if c == 104:
                self.previous_station()

            # next station on l
            if c == 108:
                self.next_station()

            # play/pause on p
            if c == 112:
                self.play_pause()

            # Stop on ctrl+c, q
            if c in (3, 113):
                raise StopApplication("User terminated app")


def demo(screen):
    scenes = [
        Scene([SomeView(screen, player)], -1, name="Station Explorer"),
    ]

    screen.play(
        scenes,
        stop_on_resize=True,
        start_scene=scenes[0],
        allow_int=True,
    )


while True:
    try:
        Screen.wrapper(demo, catch_interrupt=True)
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene
