import sys

from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication
from asciimatics.widgets import (
    Frame,
    Layout,
    Text,
)

from map.map_widget import Map


class MapView(Frame):
    def __init__(self, screen: Screen):
        super(MapView, self).__init__(
            screen,
            screen.height,
            screen.width,
            hover_focus=False,
            can_scroll=False,
            title="MapTest",
        )

        self._map = Map(name="Map", zoom=5, satellite=False)

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._map, 0)
        self.fix()


def map_test(screen: Screen):
    scenes = [
        Scene([MapView(screen)], -1, name="Station Explorer"),
    ]

    screen.play(
        scenes,
        stop_on_resize=True,
        start_scene=scenes[0],
        allow_int=True,
    )


while True:
    try:
        Screen.wrapper(map_test, catch_interrupt=True)
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene
