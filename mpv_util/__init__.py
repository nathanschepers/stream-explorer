from collections.abc import Callable

import mpv


class MPVWrapper:
    """
    A class to wrap the mpv player. Includes setting up the media-title observer.
    """

    def __init__(self):
        self.__mpv_player = mpv.MPV(
            input_default_bindings=True,
            input_vo_keyboard=True,
            video=False,
        )
        self._title_callback: Callable[[str], None] = lambda _: None

        # Decorates the title_observer function, then 'promotes' it to the instance.
        # NB: This little dance needs to be done because we only have access
        #     to the property observer decorator at run-time.
        @self.__mpv_player.property_observer("media-title")
        def title_observer(_name: str, value: str) -> None:
            # only call the callback when we are actually passed a title
            if value:
                self._title_callback(value)

        self.__title_observer = title_observer

    def register_title_callback(self, callback: Callable[[str], None]) -> None:
        self._title_callback = callback

    @property
    def player(self) -> mpv.MPV:
        return self.__mpv_player
