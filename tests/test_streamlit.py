import ui.streamlit_app as app


def test_import_and_tabs():
    assert hasattr(app, "render_monitor_tab")
    assert hasattr(app, "render_scan_tab")
