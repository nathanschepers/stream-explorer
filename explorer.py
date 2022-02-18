import sys

from waiting import wait

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
from map.map_widget import Map

# to be replaced with... something. wrote to radio.garden about API docs.
STATIONS_DB = [
    # {
    #     "name": "Radio Thiossane",
    #     "city": "Dakar",
    #     "country": "Senegal",
    #     "location": (14.716677, -17.467686),
    #     "stream": "http://listen.senemultimedia.net:8110/stream",
    # },
    # {
    #     "name": "Dr. Dick's Dub Shack",
    #     "city": "Hamilton",
    #     "country": "Bermuda",
    #     "location": (32.339008, -64.738419),
    #     "stream": "https://streamer.radio.co/s0635c8b0d/listen",
    # },
    {
        "name": "Ycoden Daute Radio",
        "city": "Icod de los Vinos",
        "country": "Spain",
        "location": (28.367571, -16.718861),
        "stream": "http://pr1cen101.emisionlocal.com:8060/live",
    },
    {
        "name": "CJAM 99.1 Windsor/Detroit",
        "city": "Windsor",
        "country": "Canada",
        "location": (42.314079, -83.036858),
        "stream": "http://stream.cjam.ca/CJAM-live-256k.mp3.m3u",
    },

]

PLAYER_HEIGHT = 5
DEFAULT_ZOOM = 10


class MapFrame(Frame):
    def __init__(self, screen: Screen, world_map: Map):
        super(MapFrame, self).__init__(
            screen,
            height=screen.height - PLAYER_HEIGHT,
            width=screen.width,
            x=0,
            y=0,
            hover_focus=False,
            can_scroll=False,
            title="Map",
        )

        self._map = world_map

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._map, 0)
        self.fix()


class PlayerFrame(Frame):
    __empty_data = {
        "station_location": "-",
        "station_name": "-",
        "artist": "-",
        "song": "-",
        "album": "-",
    }

    def __init__(self, screen: Screen, stream_player: StreamPlayer, world_map: Map):
        super(PlayerFrame, self).__init__(
            screen,
            height=PLAYER_HEIGHT,
            width=screen.width,
            x=0,
            y=screen.height - PLAYER_HEIGHT,
            on_load=self._load,
            hover_focus=True,
            can_scroll=False,
            is_modal=True,
            title="Player",
        )

        self._world_map = world_map

        self._player = stream_player
        self._player.register_songinfo_callback(self._update_song)
        self._player.register_stationinfo_callback(self._update_map_with_station)
        self._player.register_stationinfo_callback(self._update_station)

        # Label initialization (station)
        self._station_location = Text(
            label="Location:",
            name="station_location",
        )
        self._station_name = Text(
            label="Station name:",
            name="station_name",
        )

        # Label initialization (song)
        self._now_playing = Text(label="Now playing:", name="now_playing")

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
        self._player.play()
        self._world_map.force_center(*self._player.current_station["location"])
        self._player.force_callbacks()

    def _update_song(self, now_playing: str) -> None:
        """this is called from the player when new song information is available"""
        updated_song = {
            "now_playing": now_playing
        }

        self.data = updated_song

    def _update_station(self, station: dict) -> None:
        """this is called from the player when new station information is available"""
        updated_station = {
            "station_location": f"{station['city']}, {station['country']}",
            "station_name": station["name"],
        }

        self.data = updated_station

    def _update_map_with_station(self, station: dict) -> None:
        """this is called from the player when new station information is available"""

        map_data = {
            "latitude": station["location"][0],
            "longitude": station["location"][1],
            "zoom": DEFAULT_ZOOM,
        }
        self._world_map.value = map_data
        self._world_map.update(0)

    def play_pause(self):
        self._player.play_pause()

    def previous_station(self):
        self._player.previous_station()

    def next_station(self):
        self._player.next_station()

    def process_event(self, event: Event):
        if isinstance(event, KeyboardEvent):
            c = event.key_code
            # print(c)

            match c:
                case 122:
                    print(f"{self._world_map._longitude} {self._world_map._desired_longitude}")
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


# these need to be globals so we don't step on ourselves later
stream_player: StreamPlayer | None = None
world_map: Map | None = None


def initialize_player_and_map():
    global stream_player, world_map
    if not stream_player:
        stream_player = StreamPlayer(MPVWrapper(), STATIONS_DB)
    if not world_map:
        world_map = Map(name="Map", zoom=DEFAULT_ZOOM, satellite=False)
        wait(lambda: world_map.is_ready, timeout_seconds=120, waiting_for="world map")


def player(screen: Screen):
    initialize_player_and_map()
    map_frame = MapFrame(screen, world_map)
    player_frame = PlayerFrame(screen, stream_player, world_map)

    frames = [
        map_frame,
        player_frame
    ]

    scenes = [
        Scene(frames, duration=-1, clear=False, name="Station Explorer"),
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
