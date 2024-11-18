import platform
import subprocess

import cv2
import numpy as np
import pyautogui

from .image_funcs import ROI


def screen_capture(window_id, dst_path):
    subprocess.call(["screencapture", "-l", str(window_id), dst_path])


class CaptureRegionForMac(object):
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


class CaptureRegionForWin(object):

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
