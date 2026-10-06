import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from core.suggestions import Suggestion


class SuggestionRow(Gtk.Button):
    def __init__(self, suggestion: Suggestion, original_text, index, callback):
        super().__init__()

        self.index = index
        self.suggestion = suggestion

        self.add_css_class("suggestion")

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4,
        )

        original_word = original_text[suggestion.start:suggestion.end]

        replacement = (
            suggestion.replacements[0]
            if suggestion.replacements
            else ""
        )

        original = Gtk.Label(
            label=f"{original_word} → {replacement}",
        )
        original.set_xalign(0)
        original.add_css_class("suggestion-replacement")

        message = Gtk.Label(
            label=suggestion.message,
        )

        box.append(original)

        self.set_child(box)

        self.connect(
            "clicked",
            self._on_clicked,
            callback,
        )

    def _on_clicked(self, button, callback):
        callback(self.index)
