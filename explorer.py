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
        "city": "Dakar",
        "country": "Senegal",
        "location": (14.716677, -17.467686),
        "stream": "http://listen.senemultimedia.net:8110/stream",
    },
    {
        "name": "Dr. Dick's Dub Shack",
        "city": "Hamilton",
        "country": "Bermuda",
        "location": (32.339008, -64.738419),
        "stream": "https://streamer.radio.co/s0635c8b0d/listen",
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

    def __init__(self, screen: Screen, stream_player: StreamPlayer):
        super(PlayerView, self).__init__(
            screen,
            5,
            screen.width,
            on_load=self._load,
            hover_focus=True,
            can_scroll=False,
            title="Player",
        )

        self._player = stream_player
        self._player.register_songinfo_callback(self._update_song)
        self._player.register_stationinfo_callback(self._update_station)

        # Label initialization (station)
        self._station_location = Text(
            label="Location:",
            name="station_location",
            disabled=True,
        )
        self._station_name = Text(
            label="Station name:",
            name="station_name",
            disabled=True,
        )

        # Label initialization (song)
        self._now_playing = Text(label="Now playing:", name="now_playing", disabled=True)

        # set up layout and widgets
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._now_playing, 0)
        layout.add_widget(self._station_name, 0)
        layout.add_widget(self._station_location, 0)
        self.fix()

    def _load(self):
        self.data = self.__empty_data
        self.save()
        self._player.force_callbacks()
        self._player.play()

    def _update_song(self, now_playing: str) -> None:
        """this is called from the player when new song information is available"""
        updated_song = {
            "now_playing": now_playing
        }

        self.data = updated_song
        self.save()
        self.screen.force_update()

    def _update_station(self, station: dict) -> None:
        """this is called from the player when new station information is available"""
        updated_station = {
            "station_location": f"{station['city']}, {station['country']}",
            "station_name": station["name"],
        }

        self.data = updated_station
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
    stream_player = StreamPlayer(MPVWrapper(), stations_db)

    scenes = [
        Scene([PlayerView(screen, stream_player)], -1, name="Station Explorer"),
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
