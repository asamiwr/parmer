import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from core.suggestions import Suggestion
from ui.suggestion_row import SuggestionRow


def test_suggestion_row_stores_suggestion():
    suggestion = Suggestion(
        message="Use these instead.",
        start=0,
        end=4,
        replacements=["these"],
    )

    row = SuggestionRow(
        suggestion=suggestion,
        original_text="this are",
        index=0,
        callback=lambda index: None,
    )

    assert row.suggestion is suggestion
    assert row.index == 0


def test_suggestion_row_click_calls_callback():
    suggestion = Suggestion(
        message="Use these instead.",
        start=0,
        end=4,
        replacements=["these"],
    )

    clicked = []

    def callback(index):
        clicked.append(index)

    row = SuggestionRow(
        suggestion=suggestion,
        original_text="this are",
        index=3,
        callback=callback,
    )

    row._on_clicked(None, callback)

    assert clicked == [3]


def test_suggestion_row_displays_original_and_replacement():
    suggestion = Suggestion(
        message="Use these instead.",
        start=0,
        end=4,
        replacements=["these"],
    )

    row = SuggestionRow(
        suggestion=suggestion,
        original_text="this are",
        index=0,
        callback=lambda index: None,
    )

    box = row.get_child()
    label = box.get_first_child()

    assert label.get_text() == "this → these"
