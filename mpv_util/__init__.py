"""
This should probably be turned into a class, but i can't work out how to use the property_observer
on an instance method.
"""
from collections import Callable

import mpv

_title_callback = None

mpv_player = mpv.MPV(
    input_default_bindings=True,
    input_vo_keyboard=True,
    video=False,
)


@mpv_player.property_observer("media-title")
def _title_observer(_name, value):
    if value and _title_callback:
        _title_callback(value)


def register_title_callback(callback):
    global _title_callback
    _title_callback = callback


class MPVWrapper:
    def __init__(self):
        self._mpv_player = mpv.MPV(
            input_default_bindings=True,
            input_vo_keyboard=True,
            video=False,
        )
        self._title_callback: Callable = lambda _: None

        @self._mpv_player.property_observer("media-title")
        def title_observer(_name, value):
            if value and self._title_callback:
                _title_callback(value)

        self._title_observer = title_observer

    def register_title_callback(self, callback: Callable):
        self._title_callback = callback
