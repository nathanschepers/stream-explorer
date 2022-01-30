from collections import Callable

import mpv_util


class Player:
    def __init__(self, player, stations):
        self._mpv_player = player
        self._playing = False
        self._stations = stations
        self._station_index = 0
        self._songinfo_callback = lambda _: None
        self._stationinfo_callback = lambda _: None
        # this should be injected
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
