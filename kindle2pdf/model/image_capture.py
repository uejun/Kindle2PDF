from pathlib import Path
import os
import subprocess

import cv2
import numpy as np
import pyautogui


class ImageCaptureForMac:

    cache_dir_path = Path(".cache_img")
    cache_image_path = cache_dir_path.joinpath("tmp.png")

    def __init__(self, window_id, roi):
        self.window_id = window_id
        self.left = roi.left
        self.right = roi.right
        self.top = roi.top
        self.bottom = roi.bottom

        if not self.cache_dir_path.is_dir():
            self.cache_dir_path.mkdir()

    def get_current_timestamp(self):
        return self.cache_image_path.stat().st_mtime

    @classmethod
    def _screen_capture(cls, window_id):
        subprocess.call(["screencapture", "-l", str(window_id),
                         str(cls.cache_image_path)])

    def crop_capture(self):
        self._screen_capture(self.window_id)
        img = cv2.imread(str(self.cache_image_path), 1)
        return img[self.top:self.bottom, self.left:self.right]

    def close(self):
        for path in self.cache_dir_path.glob("*.png"):
            os.remove(path)


class ImageCaptureForWin:

    def __init__(self, app_window, roi):
        self.app_window = app_window
        self.roi = roi
        self.window_left, self.window_top = app_window.topleft
        self.window_width, self.window_height = app_window.size

    def crop_capture(self):
        # アプリケーションウィンドウをキャプチャ
        screenshot = pyautogui.screenshot(
            region=(self.window_left, self.window_top, self.window_width, self.window_height))
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        # ROIでクロップ
        roi_img = img[int(self.roi.top):int(self.roi.bottom), int(self.roi.left):int(self.roi.right)]
        return roi_img

