import cv2


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

