import subprocess
from subprocess import Popen, PIPE
import time

import pyautogui


class PagerForMac(object):

    # Script Example
    """
    tell application \"Kindle\"
        activate
        tell application \"System Events\"
            key code 124
        end tell
    end tell
    """

    def __init__(self, app_name, direction="right"):
        self.app_name = app_name
        self.direction = direction
        self._script = self._paging_script(app_name, direction)
        self.current_index = 0

    def go_next(self):

        args = []
        p = Popen(['/usr/bin/osascript', '-'] + args,
                  stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(self._script.encode('utf-8'))
        print(stdout.decode())
        print(stderr.decode())

    @classmethod
    def _paging_script(cls, app_name="Kindle", direction="right"):
        """
        Create Script for Pagination

        Args:
            app_name: Kindle etc.
            direction: prev or next

        Returns:
            script: str
        """
        if direction == 'left':
            key_code = "123"
        elif direction == 'right':
            key_code = "124"
        else:
            raise ValueError("unknown direction")
        script = "tell application \"Kindle\""
        script += "\n    activate"
        script += "\nend tell"
        script += "\n delay 1"
        script += "\n tell application \"System Events\""
        script += "\n    tell process " + "\"" + app_name + "\""
        script += "\n        key code " + key_code
        script += "\n    end tell"
        script += "\n end tell"

        # script = "tell process " + "\"" + app_name + "\""
        # script += "\n    activate"
        # script += "\n    tell application \"System Events\""
        # script += "\n        key code " + key_code
        # script += "\n    end tell"
        # script += "\nend tell"

        return script


class PagerForWin(object):
    def __init__(self, app_window, direction="right"):
        self.app_window = app_window
        self.direction = direction
        self.current_index = 0

    def go_next(self):
        # アプリケーションウィンドウをアクティブに
        self.app_window.activate()
        time.sleep(0.5)  # ウィンドウが前面に来るのを待つ
        if self.direction == 'right':
            pyautogui.press('right')
        elif self.direction == 'left':
            pyautogui.press('left')
        else:
            raise ValueError("Unknown direction")
