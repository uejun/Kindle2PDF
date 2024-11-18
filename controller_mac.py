import os
from pathlib import Path
import subprocess
from subprocess import Popen, PIPE
import time
import cv2
import numpy as np

from window import WindowManager
from pdf import PDFWriter


def is_same_img(img1, img2):
    # 全く同じだったらゼロ画像になるはず
    mask = cv2.absdiff(img1, img2)
    mask_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    # 全く同じだったらゼロじゃないところをカウントするとゼロになるはず．
    return not cv2.countNonZero(mask_gray)


class ROI(object):
    def __init__(self, left, right, top, bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top


class CaptureRegion(object):
    def __init__(self):
        self.popup_window_resize_rate = 1.5

        self.roi = None

    def select(self, image_path):
        """
        ポップアップウィンドウを提示してROIをユーザーに指定してもらう
        :param image_path:
        :return:
        """
        org_img = cv2.imread(image_path)
        width = org_img.shape[1]
        height = org_img.shape[0]

        # 普通に表示するとディスプレイよりも大きい画像が表示されるので
        # 縮小して表示する
        view_w = int(width/self.popup_window_resize_rate)
        view_h = int(height/self.popup_window_resize_rate)
        img = cv2.resize(org_img, (view_w, view_h))

        # ROIの指定を待つ
        region = cv2.selectROI(img)

        left = int(region[0] * self.popup_window_resize_rate)
        right = int((region[0] + region[2]) * self.popup_window_resize_rate)
        top = int(region[1] * self.popup_window_resize_rate)
        bottom = int((region[1] + region[3]) * self.popup_window_resize_rate)

        self.roi = ROI(left, right, top, bottom)


def _screen_capture(window_id, dst_path):
    subprocess.call(["screencapture", "-l", str(window_id), dst_path])


class ImageCapture:

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


class Pager(object):

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


class CaptureController(object):
    def __init__(self, app_name, direction):
        self.app_name = app_name
        self.pager = Pager(app_name, direction)

        self.previous_timestamp = None

    def start(self):

        MAX_PAGE = 3000

        # Retrieve window id of the application.
        window_id = WindowManager.get_window_id(self.app_name)
        print(self.app_name, "Window", window_id)
        capture_image_path = ".cache_img/tmp.png"
        Path(capture_image_path).parent.mkdir(exist_ok=True, parents=True)
        _screen_capture(window_id, capture_image_path)

        # Specify the capture area.
        region = CaptureRegion()
        region.select(capture_image_path)

        # ImageCapture
        cap = ImageCapture(window_id, region.roi)

        pdf_writer = PDFWriter()

        current_img = np.zeros((region.roi.height, region.roi.width, 3),
                               dtype=np.uint8)
        for i in range(0, MAX_PAGE):

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

            # 1ページごとに画像をPDFに変換し，ローカルに保存
            filename = str(i) + ".pdf"

            pdf_writer.save_as_pdf(crop_img, filename)

            # 本ページ画像をキャッシュしておく
            current_img = crop_img.copy()

            self.previous_timestamp = cap.get_current_timestamp()

        # すべてのPDFを統合して，一つのPDFとする
        save_path = Path(os.path.join("dist", "result.pdf"))
        pdf_writer.merge(save_path)

        # ページごとのPDFを削除する
        pdf_writer.close()
        cap.close()

