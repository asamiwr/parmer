from core.position import relative_to_monitor, position_popup


class PopupController:
    def __init__(self, display):
        self.display = display
        self.apply_callback = None

    def on_apply_requested(self, callback):
        self.apply_callback = callback

    def get_monitor(self, x, y):
        monitors = self.display.get_monitors()

        for i in range(monitors.get_n_items()):
            monitor = monitors.get_item(i)
            geometry = monitor.get_geometry()

            if (
                geometry.x <= x < geometry.x + geometry.width
                and geometry.y <= y < geometry.y + geometry.height
            ):
                return monitor

        return None

    def get_position(self, caret, popup_width, popup_height):
        monitor = self.get_monitor(caret.x, caret.y)

        if monitor is None:
            return None

        geometry = monitor.get_geometry()

        relative_caret = relative_to_monitor(
            caret,
            monitor_x=geometry.x,
            monitor_y=geometry.y,
        )

        position = position_popup(
            relative_caret,
            popup_width=popup_width,
            popup_height=popup_height,
            screen_width=geometry.width,
            screen_height=geometry.height,
        )

        return monitor, position

    def show(self, popup, caret, popup_width, popup_height, suggestions, original_text):
        result = self.get_position(
            caret,
            popup_width=popup_width,
            popup_height=popup_height,
        )

        if result is None:
            return False

        monitor, position = result

        geometry = monitor.get_geometry()

        print(
            f"Popup: "
            f"caret=({caret.x}, {caret.y}) "
            f"monitor=({geometry.x}, {geometry.y}, "
            f"{geometry.width}x{geometry.height}) "
            f"position=({position.x}, {position.y})"
        )

        if self.apply_callback is not None:
            popup.on_apply_requested(self.apply_callback)

        popup.show(monitor, position, suggestions, original_text)

        return True

    def show_at_caret(self, popup, caret, suggestions, original_text):
        return self.show(popup, caret, popup_width=320, popup_height=100, suggestions=suggestions, original_text=original_text)
