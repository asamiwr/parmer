from ui.backends.layer_shell import LayerShellBackend


class FakeWindow:
    def __init__(self, application):
        self.application = application
        self.child = None
        self.presented = False
        self.closed = False

    def set_default_size(self, width, height):
        self.default_size = (width, height)

    def set_child(self, child):
        self.child = child

    def get_child(self):
        return self.child

    def present(self):
        self.presented = True

    def close(self):
        self.closed = True


class FakeSuggestionRow:
    def __init__(self, suggestion, original_text, index, callback):
        self.suggestion = suggestion
        self.original_text = original_text
        self.index = index
        self.callback = callback
        self.next_sibling = None

    def set_halign(self, align):
        self.halign = align

    def get_next_sibling(self):
        return self.next_sibling


class FakeBox:
    def __init__(self, **kwargs):
        self.children = []

    def add_css_class(self, name):
        self.css_class = name

    def set_margin_top(self, value):
        self.margin_top = value

    def set_margin_bottom(self, value):
        self.margin_bottom = value

    def set_margin_start(self, value):
        self.margin_start = value

    def set_margin_end(self, value):
        self.margin_end = value

    def append(self, child):
        if self.children:
            self.children[-1].next_sibling = child

        self.children.append(child)

    def get_first_child(self):
        if not self.children:
            return None

        return self.children[0]

    def remove(self, child):
        index = self.children.index(child)

        previous = (
            self.children[index - 1]
            if index > 0
            else None
        )

        next_child = (
            self.children[index + 1]
            if index + 1 < len(self.children)
            else None
        )

        if previous is not None:
            previous.next_sibling = next_child

        self.children.remove(child)

        child.next_sibling = None


class FakeOrientation:
    VERTICAL = 0


class FakeAlign:
    FILL = 0


class FakeEdge:
    TOP = 0
    LEFT = 1


class FakeLayer:
    TOP = "top"
    OVERLAY = "overlay"


def setup_layer_shell_mocks(monkeypatch):
    created_windows = []
    created_rows = []

    def fake_window(application):
        window = FakeWindow(application)
        created_windows.append(window)
        return window

    def fake_row(suggestion, original_text, index, callback):
        row = FakeSuggestionRow(
            suggestion,
            original_text,
            index,
            callback,
        )
        created_rows.append(row)
        return row

    fake_gtk = type(
        "FakeGtk",
        (),
        {
            "Window": staticmethod(fake_window),
            "Box": FakeBox,
            "Orientation": FakeOrientation,
            "Align": FakeAlign,
        },
    )

    monkeypatch.setattr(
        "ui.backends.layer_shell.Gtk",
        fake_gtk,
    )

    monkeypatch.setattr(
        "ui.backends.layer_shell.SuggestionRow",
        fake_row,
    )

    monkeypatch.setattr(
        "ui.backends.layer_shell.LayerShell.init_for_window",
        lambda window: None,
    )

    monkeypatch.setattr(
        "ui.backends.layer_shell.LayerShell.set_namespace",
        lambda window, namespace: None,
    )

    monkeypatch.setattr(
        "ui.backends.layer_shell.LayerShell.set_layer",
        lambda window, layer: None,
    )

    monkeypatch.setattr(
        "ui.backends.layer_shell.LayerShell.set_monitor",
        lambda window, monitor: None,
    )

    monkeypatch.setattr(
        "ui.backends.layer_shell.LayerShell.set_anchor",
        lambda window, edge, value: None,
    )

    monkeypatch.setattr(
        "ui.backends.layer_shell.LayerShell.set_margin",
        lambda window, edge, value: None,
    )

    monkeypatch.setattr(
        "ui.backends.layer_shell.LayerShell",
        type(
            "FakeLayerShell",
            (),
            {
                "Layer": FakeLayer,
                "Edge": FakeEdge,
                "init_for_window": staticmethod(
                    lambda window: None
                ),
                "set_namespace": staticmethod(
                    lambda window, namespace: None
                ),
                "set_layer": staticmethod(
                    lambda window, layer: None
                ),
                "set_monitor": staticmethod(
                    lambda window, monitor: None
                ),
                "set_anchor": staticmethod(
                    lambda window, edge, value: None
                ),
                "set_margin": staticmethod(
                    lambda window, edge, value: None
                ),
            },
        ),
    )

    return created_windows, created_rows


def make_position(x=100, y=200):
    return type(
        "Position",
        (),
        {
            "x": x,
            "y": y,
        },
    )()


def test_suggestion_click_calls_apply_callback():
    backend = LayerShellBackend(application=None)

    clicked = []

    def callback(index):
        clicked.append(index)

    backend.on_apply_requested(callback)

    backend._on_suggestion_clicked(2)

    assert clicked == [2]


def test_apply_callback_can_be_registered_and_replaced():
    backend = LayerShellBackend(application=None)

    first = []
    second = []

    backend.on_apply_requested(
        lambda index: first.append(index)
    )

    backend._on_suggestion_clicked(1)

    backend.on_apply_requested(
        lambda index: second.append(index)
    )

    backend._on_suggestion_clicked(3)

    assert first == [1]
    assert second == [3]

def test_show_creates_window_once(monkeypatch):
    backend = LayerShellBackend(application=object())

    created_windows, _ = setup_layer_shell_mocks(
        monkeypatch,
    )

    monitor = object()
    position = make_position()
    suggestions = [object()]

    backend.show(
        monitor,
        position,
        suggestions,
        original_text="this are",
    )

    first_window = backend.window

    backend.show(
        monitor,
        position,
        suggestions,
        original_text="this are",
    )

    second_window = backend.window

    assert first_window is second_window
    assert len(created_windows) == 1


def test_show_updates_suggestions(monkeypatch):
    backend = LayerShellBackend(application=object())

    _, created_rows = setup_layer_shell_mocks(
        monkeypatch,
    )

    monitor = object()
    position = make_position()

    first_suggestions = [
        object(),
        object(),
    ]

    second_suggestions = [
        object(),
    ]

    backend.show(
        monitor,
        position,
        first_suggestions,
        original_text="this are",
    )

    assert len(created_rows) == 2
    assert created_rows[0].suggestion is first_suggestions[0]
    assert created_rows[1].suggestion is first_suggestions[1]

    backend.show(
        monitor,
        position,
        second_suggestions,
        original_text="this are",
    )

    assert len(created_rows) == 3
    assert created_rows[2].suggestion is second_suggestions[0]

    assert backend.content_box.children == [
        created_rows[2],
    ]


def test_show_updates_window_position(monkeypatch):
    backend = LayerShellBackend(application=object())

    setup_layer_shell_mocks(monkeypatch)

    monitor = object()
    position = make_position(
        x=120,
        y=240,
    )
    suggestions = [object()]

    backend.show(
        monitor,
        position,
        suggestions,
        original_text="this are",
    )

    assert backend.window is not None


def test_hide_closes_window(monkeypatch):
    backend = LayerShellBackend(application=object())

    created_windows, _ = setup_layer_shell_mocks(
        monkeypatch,
    )

    monitor = object()
    position = make_position()
    suggestions = [object()]

    backend.show(
        monitor,
        position,
        suggestions,
        original_text="this are",
    )

    window = backend.window

    assert window is created_windows[0]

    backend.hide()

    assert window.closed is True
    assert backend.window is None


def test_hide_without_window_does_nothing():
    backend = LayerShellBackend(application=None)

    backend.hide()

    assert backend.window is None
