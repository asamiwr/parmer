import accessibility.atspi as atspi


def test_set_popup_ui_registers_apply_callback():
    class FakePopupController:
        def __init__(self):
            self.callback = None

        def on_apply_requested(self, callback):
            self.callback = callback

    controller = FakePopupController()
    popup = object()

    atspi.set_popup_ui(controller, popup)

    assert atspi.popup_controller is controller
    assert atspi.popup is popup
    assert atspi.popup_controller.callback is atspi.on_apply_requested

def test_on_text_checked_shows_popup(monkeypatch):
    shown = []

    class FakePopupController:
        def show_at_caret(
            self,
            popup,
            caret,
            suggestions,
            original_text,
        ):
            shown.append(
                (
                    popup,
                    caret,
                    suggestions,
                    original_text,
                )
            )

    popup = object()
    controller = FakePopupController()

    monkeypatch.setattr(atspi, "popup_controller", controller)
    monkeypatch.setattr(atspi, "popup", popup)

    obj = object()
    atspi.session.set_object(obj)

    atspi.tracker.text = "this are amir"
    context = atspi.tracker.get_context()

    generation = atspi.session.get_snapshot()["generation"]

    from core.suggestions import Suggestion

    suggestions = [
        Suggestion(
            message="Use these instead.",
            start=0,
            end=4,
            replacements=["these"],
        )
    ]

    request = atspi.CheckRequest(
        context=context,
        generation=generation,
    )

    from core.position import Rect

    monkeypatch.setattr(
        atspi,
        "get_caret_rect",
        lambda obj: Rect(
            x=100,
            y=200,
            width=7,
            height=22,
        ),
    )

    atspi.on_text_checked(suggestions, request)

    assert len(shown) == 1

    shown_popup, caret, shown_suggestions, original_text = shown[0]
    assert original_text == "this are amir"

    assert shown_popup is popup

    assert caret.x == 100
    assert caret.y == 200
    assert caret.width == 7
    assert caret.height == 22

    assert shown_suggestions == suggestions


def test_caret_move_repositions_popup(monkeypatch):
    shown = []

    class FakePopupController:
        def show_at_caret(
            self,
            popup,
            caret,
            suggestions,
            original_text,
        ):
            shown.append(
                (
                    popup,
                    caret,
                    suggestions,
                    original_text,
                )
            )

    popup = object()
    controller = FakePopupController()

    monkeypatch.setattr(atspi, "popup_controller", controller)
    monkeypatch.setattr(atspi, "popup", popup)

    obj = object()
    atspi.session.set_object(obj)

    atspi.tracker.text = "this are amir"
    context = atspi.tracker.get_context()

    from core.suggestions import Suggestion
    from core.position import Rect

    suggestions = [
        Suggestion(
            message="Use these instead.",
            start=0,
            end=4,
            replacements=["these"],
        )
    ]

    generation = atspi.session.get_snapshot()["generation"]

    atspi.session.update_suggestions(
        context,
        suggestions,
        generation,
    )

    monkeypatch.setattr(
        atspi,
        "get_caret_rect",
        lambda obj: Rect(
            x=300,
            y=400,
            width=7,
            height=22,
        ),
    )

    class FakeEvent:
        source = obj
        type = "object:text-caret-moved"

    monkeypatch.setattr(
        atspi,
        "should_handle",
        lambda event: True,
    )

    monkeypatch.setattr(
        atspi,
        "is_text_field",
        lambda obj: True,
    )

    atspi.on_event(FakeEvent())

    assert len(shown) == 1

    shown_popup, caret, shown_suggestions, original_text = shown[0]
    assert original_text == "this are amir"

    assert shown_popup is popup
    assert caret.x == 300
    assert caret.y == 400
    assert shown_suggestions == suggestions


def test_on_text_checked_hides_popup_when_no_suggestions(monkeypatch):
    hidden = []

    class FakePopup:
        def hide(self):
            hidden.append(True)

    popup = FakePopup()

    monkeypatch.setattr(atspi, "popup", popup)

    atspi.tracker.text = "this are amir"
    context = atspi.tracker.get_context()

    generation = atspi.session.get_snapshot()["generation"]

    from core.suggestions import Suggestion

    old_suggestions = [
        Suggestion(
            message="Use these instead.",
            start=0,
            end=4,
            replacements=["these"],
        )
    ]

    atspi.session.update_suggestions(
        context,
        old_suggestions,
        generation,
    )

    request = atspi.CheckRequest(
        context=context,
        generation=generation,
    )

    atspi.on_text_checked([], request)

    assert hidden == [True]
