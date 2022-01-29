import mpv

title_callback = None

player = mpv.MPV(
    input_default_bindings=True,
    input_vo_keyboard=True,
    video=False,
)


def set_title_callback(callback):
    global title_callback
    title_callback = callback


@player.property_observer("media-title")
def _title_observer(_name, value):
    if value and title_callback:
        title_callback(value)
