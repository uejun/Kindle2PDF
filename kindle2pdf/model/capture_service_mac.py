import os
from pathlib import Path
import subprocess
from subprocess import Popen, PIPE
import time
import cv2
import numpy as np


from .capture_region import screen_capture, CaptureRegionForMac
from .image_capture import ImageCaptureForMac
from .image_funcs import is_same_img
from .pager import PagerForMac
from .page_writer import OutputFormat
from .window import WindowManager
from .capture_service import CaptureServiceBase


class CaptureControllerForMac(CaptureServiceBase):

    def __init__(self, app_name, direction, save_format: OutputFormat):
        super().__init__(app_name, direction, save_format)

    def run(self):

        # Retrieve window id of the application.
        window_id = WindowManager.get_window_id(self.app_name)
        print(self.app_name, "Window", window_id)
        capture_image_path = ".cache_img/tmp.png"
        Path(capture_image_path).parent.mkdir(exist_ok=True, parents=True)
        screen_capture(window_id, capture_image_path)

        # Specify the capture area.
        region = CaptureRegionForMac()
        region.select(capture_image_path)

        # ImageCapture
        cap = ImageCaptureForMac(window_id, region.roi)

        current_img = np.zeros((region.roi.height, region.roi.width, 3),
                               dtype=np.uint8)

        self.pager = PagerForMac(self.app_name, self.direction)
        self.previous_timestamp = None

        for i in range(0, self.MAX_PAGE):

            # ページをめくる
            self.pager.go_next()

            # 別プロセスで画像の保存とページめくりを行うので,
            # ちゃんと前のキャプチャが保存されるかを確認する
            if self.previous_timestamp is not None:
                if self.previous_timestamp == cap.get_current_timestamp():
                    time.sleep(3.0)

            # キャプチャ画像を取得
            crop_img = cap.crop_capture()

            # 前ページと同じかどうかチェック
            # 同じ場合は終了
            if i > 1 and is_same_img(current_img, crop_img):
                print("Done because of same image.")
                break

            # 1ページごとに画像を保存
            basename = str(i)
            self.writer.save(crop_img, basename)

            # 本ページ画像をキャッシュしておく
            current_img = crop_img.copy()

            self.previous_timestamp = cap.get_current_timestamp()

        # すべてのPDFを統合して，一つのPDFとする
        self.writer.handle_finish()

        cap.close()

