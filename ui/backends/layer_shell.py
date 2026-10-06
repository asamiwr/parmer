from ctypes import CDLL

CDLL("libgtk4-layer-shell.so")

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")

from gi.repository import Gtk
from gi.repository import Gtk4LayerShell as LayerShell

from ui.suggestion_row import SuggestionRow


class LayerShellBackend:
    def __init__(self, application):
        self.application = application
        self.window = None
        self.content_box = None
        self.apply_callback = None

    def on_apply_requested(self, callback):
        self.apply_callback = callback

    def _on_suggestion_clicked(self, index):
        print(f"Suggestion clicked: {index}")

        if self.apply_callback is not None:
            self.apply_callback(index)

    def _update_content(self, suggestions, original_text):
        if self.content_box is None:
            self.content_box = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=8,
            )

            self.content_box.add_css_class("popup-content")

            self.content_box.set_margin_top(12)
            self.content_box.set_margin_bottom(12)
            self.content_box.set_margin_start(12)
            self.content_box.set_margin_end(12)

        box = self.content_box

        child = box.get_first_child()

        while child is not None:
            next_child = child.get_next_sibling()
            box.remove(child)
            child = next_child

        for index, suggestion in enumerate(suggestions):
            row = SuggestionRow(
                suggestion=suggestion,
                original_text=original_text,
                index=index,
                callback=self._on_suggestion_clicked,
            )

            row.set_halign(Gtk.Align.FILL)
            box.append(row)

        return box

    def show(self, monitor, position, suggestions, original_text):
        if self.window is None:
            window = Gtk.Window(application=self.application)
            window.set_default_size(320, 100)

            LayerShell.init_for_window(window)
            LayerShell.set_namespace(window, "parmer-popup")
            LayerShell.set_layer(window, LayerShell.Layer.TOP)
            LayerShell.set_monitor(window, monitor)

            LayerShell.set_anchor(
                window,
                LayerShell.Edge.TOP,
                True,
            )

            LayerShell.set_anchor(
                window,
                LayerShell.Edge.LEFT,
                True,
            )

            self.window = window

        window = self.window

        LayerShell.set_monitor(
            window,
            monitor,
        )

        LayerShell.set_margin(
            window,
            LayerShell.Edge.TOP,
            position.y,
        )

        LayerShell.set_margin(
            window,
            LayerShell.Edge.LEFT,
            position.x,
        )

        content = self._update_content(suggestions, original_text)

        if window.get_child() is None:
            window.set_child(content)

        window.present()

#         print(
#
#             "LayerShell margins:",
#             LayerShell.get_margin(window, LayerShell.Edge.TOP),
#             LayerShell.get_margin(window, LayerShell.Edge.LEFT),
#         )

    def hide(self):
        if self.window is not None:
            self.window.close()
            self.window = None
