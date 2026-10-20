from unittest.mock import Mock

from app.desktop_governed_floating_image_viewer import (
    DesktopGovernedFloatingImageViewer,
)


def test_manual_close_notifies_preview_cancellation():
    root = Mock()
    toolkit = Mock()
    on_close = Mock()

    viewer = DesktopGovernedFloatingImageViewer(
        root=root,
        toolkit=toolkit,
        on_close=on_close,
    )

    viewer.open((object(),))

    window = toolkit.Toplevel.return_value
    callback = window.protocol.call_args.args[1]

    callback()

    on_close.assert_called_once_with()
    window.destroy.assert_called_once_with()
    assert viewer.artifacts == ()


def test_repeated_close_does_not_repeat_notification():
    root = Mock()
    toolkit = Mock()
    on_close = Mock()

    viewer = DesktopGovernedFloatingImageViewer(
        root=root,
        toolkit=toolkit,
        on_close=on_close,
    )

    viewer.open((object(),))
    viewer.close()
    viewer.close()

    on_close.assert_called_once_with()
