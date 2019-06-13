from window import WindowManager


def test_retrieve_window_list():
    app_name = 'Kindle'
    window_id = WindowManager.get_window_id(app_name)
    print("Window ID: ", window_id)