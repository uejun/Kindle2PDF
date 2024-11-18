import os
import time
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
import pyautogui
import pygetwindow as gw
from pdfrw import PdfReader, PdfWriter


def is_same_img(img1, img2):
    # 画像の差分を計算
    mask = cv2.absdiff(img1, img2)
    mask_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    # 非ゼロピクセルをカウント
    return not cv2.countNonZero(mask_gray)


class ROI(object):
    def __init__(self, left, right, top, bottom):
        self.left = int(left)
        self.right = int(right)
        self.top = int(top)
        self.bottom = int(bottom)

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

    def select(self, app_window):
        """
        ポップアップウィンドウを提示してROIをユーザーに指定してもらう
        """
        # アプリケーションウィンドウのスクリーンショットを取得
        left, top = app_window.topleft
        width, height = app_window.size
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        # OpenCV形式に変換
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # 画像をリサイズして表示
        view_w = int(width / self.popup_window_resize_rate)
        view_h = int(height / self.popup_window_resize_rate)
        img_resized = cv2.resize(img, (view_w, view_h))

        # ROIの指定を待つ
        region = cv2.selectROI("Select ROI", img_resized)
        cv2.destroyWindow("Select ROI")

        left = region[0] * self.popup_window_resize_rate
        top = region[1] * self.popup_window_resize_rate
        width = region[2] * self.popup_window_resize_rate
        height = region[3] * self.popup_window_resize_rate

        self.roi = ROI(left, left + width, top, top + height)


class ImageCapture:
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


class Pager(object):
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


class PDFWriter(object):
    def __init__(self):
        self.cache_dir_path = Path(".cache_pdf")
        if not self.cache_dir_path.is_dir() or not self.cache_dir_path.exists():
            self.cache_dir_path.mkdir()

    def save_as_pdf(self, img, filename):
        img_pillow = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        save_path = self.cache_dir_path.joinpath(filename)
        img_pillow.save(str(save_path), "PDF", quality=100)

    def merge(self, save_path: Path):
        writer = PdfWriter()

        pdf_numbers = [int(path.stem)
                       for path in self.cache_dir_path.glob("*.pdf")]

        pdf_paths = [self.cache_dir_path.joinpath(str(pdf_num) + '.pdf')
                     for pdf_num in sorted(pdf_numbers)]

        for pdf_path in pdf_paths:
            writer.addpages(PdfReader(str(pdf_path)).pages)

        writer.write(str(save_path))

    def close(self):
        for path in self.cache_dir_path.glob("*.pdf"):
            os.remove(path)


class CaptureController(object):
    def __init__(self, app_name, direction):
        self.app_name = app_name
        self.direction = direction
        self.pager = None

    def get_window_by_title(self, title):
        """
        指定したタイトルを含むウィンドウを取得
        """
        all_windows = gw.getAllWindows()
        for window in all_windows:
            if title in window.title:
                return window
        raise ValueError(f"No window found with title containing '{title}'")


    def start(self):
        MAX_PAGE = 3000

        # アプリケーションウィンドウを取得
        try:
            app_window = self.get_window_by_title(self.app_name)
        except ValueError as e:
            print(e)
            return

        print(self.app_name, "Window", app_window)

        # ROI選択用にウィンドウの画像をキャプチャ
        left, top = app_window.topleft
        width, height = app_window.size
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        # 一時保存
        capture_image_path = ".cache_img/tmp.png"
        Path(capture_image_path).parent.mkdir(exist_ok=True, parents=True)
        cv2.imwrite(capture_image_path, screenshot_cv)

        # キャプチャ領域を指定
        region = CaptureRegion()
        region.select(app_window)

        # ImageCapture
        cap = ImageCapture(app_window, region.roi)

        pdf_writer = PDFWriter()

        current_img = np.zeros((int(region.roi.height), int(region.roi.width), 3),
                               dtype=np.uint8)
        self.pager = Pager(app_window, self.direction)
        for i in range(0, MAX_PAGE):

            # ページをめくる
            self.pager.go_next()
            time.sleep(1)  # ページが読み込まれるのを待つ

            # 画像をキャプチャ
            crop_img = cap.crop_capture()

            # 前ページと同じかどうかチェック
            if i > 0 and is_same_img(current_img, crop_img):
                print("Done because of same image.")
                break

            # PDFとして保存
            filename = str(i) + ".pdf"
            pdf_writer.save_as_pdf(crop_img, filename)

            # 現在の画像を更新
            current_img = crop_img.copy()

        # すべてのPDFを統合
        save_path = Path(os.path.join("dist", "result.pdf"))
        save_path.parent.mkdir(exist_ok=True, parents=True)
        pdf_writer.merge(save_path)

        # 後処理
        pdf_writer.close()
        print(f"PDF saved to {save_path}")


# 実行例
if __name__ == "__main__":
    app_name = "Kindle"  # キャプチャしたいアプリケーション名を指定
    direction = "right"  # ページ送りの方向を指定
    controller = CaptureController(app_name, direction)
    controller.start()
