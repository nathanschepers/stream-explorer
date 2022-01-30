from collections.abc import Callable

from mpv_util import MPVWrapper


class StreamPlayer:
    def __init__(self, wrapper: MPVWrapper, stations: list[dict[str, str | list[str]]]):
        # get the player and register the callback into this class
        self._mpv_player = wrapper.player
        wrapper.register_title_callback(self._song_callbacks)

        # set player state
        self._playing = False
        self._stations = stations
        self._station_index = 0
        self._last_songinfo = "-"

        # initialize callbacks
        self._songinfo_callbacks: [Callable[[dict], None]] = [
            lambda _: None,
        ]
        self._stationinfo_callbacks: [Callable[[dict], None]] = [
            lambda _: None,
        ]

    def register_songinfo_callback(self, callback: Callable[[str], None]) -> None:
        # register a songinfo callback
        self._songinfo_callbacks.append(callback)

    def register_stationinfo_callback(self, callback: Callable[[dict], None]) -> None:
        # register a stationinfo callback
        self._stationinfo_callbacks.append(callback)

    def force_callbacks(self) -> None:
        self._song_callbacks(self._last_songinfo)
        self._station_callbacks()

    def _song_callbacks(self, songinfo: str) -> None:
        """
        Calls the registered songinfo callbacks.
        NB: This function is also registered as the song title observer callback from mpv
        """
        self._last_songinfo = songinfo
        for callback in self._songinfo_callbacks:
            callback(songinfo)

    def _station_callbacks(self) -> None:
        # calls the registered stationinfo callback
        for callback in self._stationinfo_callbacks:
            callback(self.current_station)

    @property
    def current_station(self) -> dict[str, str]:
        # returns the current station information in a dictionary
        return self._stations[self._station_index]

    def play(self) -> None:
        # play the currently selected stream
        self._mpv_player.play(self._stations[self._station_index]["stream"])
        self._playing = True

    def pause(self) -> None:
        # pause the current stream
        self._mpv_player.stop()
        self._last_songinfo = "-"
        self._playing = False

    def play_pause(self) -> None:
        # play/pause the stream
        self.play() if not self._playing else self.pause()

    def next_station(self) -> None:
        # select the next station from the list and play it
        self._station_index = (self._station_index + 1) % len(self._stations)
        self._last_songinfo = "-"
        self._station_callbacks()
        self.play()

    def previous_station(self) -> None:
        # select the previous station from the list and play it
        self._station_index = (self._station_index - 1) % len(self._stations)
        self._last_songinfo = "-"
        self._station_callbacks()
        self.play()
