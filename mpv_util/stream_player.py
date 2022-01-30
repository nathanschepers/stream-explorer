from collections.abc import Callable

from mpv_util import MPVWrapper


class StreamPlayer:
    def __init__(self, wrapper: MPVWrapper, stations: list[dict[str, str | list[str]]]):
        # get the player and register the callback into this class
        self._mpv_player = wrapper.player
        wrapper.register_title_callback(self._update_songinfo)

        # set player state
        self._playing = False
        self._stations = stations
        self._station_index = 0

        # initialize callbacks to UI
        self._songinfo_callback: Callable[[dict[str, str]], None] = lambda _: None
        self._stationinfo_callback: Callable[[dict[str, str]], None] = lambda _: None

    def register_songinfo_callback(
        self, callback: Callable[[dict[str, str]], None]
    ) -> None:
        # register the songinfo callback to the UI
        self._songinfo_callback = callback

    def register_stationinfo_callback(
        self, callback: Callable[[dict[str, str]], None]
    ) -> None:
        # register the stationinfo callback to the UI
        self._stationinfo_callback = callback

    def force_update(self) -> None:
        self._update_stationinfo()

    def _update_songinfo(self, songinfo: str) -> None:
        """
        Calls the registered songinfo callback.
        NB: This function is registered as the song title observer from mpv
        """
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
        # calls the registered stationinfo callback
        self._stationinfo_callback(self.current_station)

    @property
    def current_station(self) -> dict[str, str]:
        # returns the current station information in a dictionary
        return {
            "station_location": self._stations[self._station_index]["country"],
            "station_name": self._stations[self._station_index]["name"],
        }

    def play(self) -> None:
        # play the currently selected stream
        self._mpv_player.play(self._stations[self._station_index]["stream"])
        self._playing = True

    def pause(self) -> None:
        # pause the current stream
        self._mpv_player.stop()
        self._playing = False

    def play_pause(self) -> None:
        # play/pause the stream
        self.play() if not self._playing else self.pause()

    def next_station(self) -> None:
        # select the next station from the list and play it
        self._station_index = (self._station_index + 1) % len(self._stations)
        self._update_stationinfo()
        self.play()

    def previous_station(self) -> None:
        # select the previous station from the list and play it
        self._station_index = (self._station_index - 1) % len(self._stations)
        self._update_stationinfo()
        self.play()
