import os
import time
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
import pyautogui
import pygetwindow as gw

from .image_funcs import is_same_img
from .pager import PagerForWin
from .page_writer import OutputFormat
from .capture_region import CaptureRegionForWin
from .image_capture import ImageCaptureForWin
from .capture_service import CaptureServiceBase


class CaptureControllerForWin(CaptureServiceBase):

    def __init__(self, app_name, direction, save_format: OutputFormat):
        super().__init__(app_name, direction, save_format)

    def run(self):

        #アプリケーションウィンドウを取得
        app_window = self.select_window_by_mouse()
        print(f"WindowObject of {self.app_name} is ", app_window)

        # ROI選択用にウィンドウの画像をキャプチャ
        left, top = app_window.topleft
        width, height = app_window.size
        print(f"Capture Region: left={left}, top={top}, width={width}, height={height}")
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # 一時保存
        capture_image_path = ".cache_img/tmp.png"
        Path(capture_image_path).parent.mkdir(exist_ok=True, parents=True)
        cv2.imwrite(capture_image_path, screenshot_cv)

        # キャプチャ領域を指定
        region = CaptureRegionForWin()
        region.select(app_window)

        # ImageCapture
        cap = ImageCaptureForWin(app_window, region.roi)

        current_img = np.zeros((int(region.roi.height), int(region.roi.width), 3),
                               dtype=np.uint8)

        self.pager = PagerForWin(app_window, self.direction)

        for i in range(0, self.MAX_PAGE):

            # ページをめくる
            self.pager.go_next()
            time.sleep(1)  # ページが読み込まれるのを待つ

            # 画像をキャプチャ
            crop_img = cap.crop_capture()

            # 前ページと同じかどうかチェック
            if i > 0 and is_same_img(current_img, crop_img):
                print("Done because of same image.")
                break

            # ページを保存
            basename = str(i)
            self.writer.save(crop_img, basename)

            # 現在の画像を更新
            current_img = crop_img.copy()

        self.writer.handle_finish()

    def select_window_by_title(self, title):
        """
        指定したタイトルを含むウィンドウを取得
        """
        all_windows = gw.getAllWindows()
        for window in all_windows:
            print(window)
            if title in window.title:
                return window
        raise ValueError(f"No window found with title containing '{title}'")

    def select_window_by_mouse(self):
        # x秒待機してアクティブウィンドウを取得
        time.sleep(5)
        # アクティブウィンドウを取得
        active_window = gw.getActiveWindow()
        return active_window