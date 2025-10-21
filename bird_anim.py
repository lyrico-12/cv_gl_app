import cv2
import time

class BirdAnimator:
    def __init__(self, size=(120, 120), switch_interval=0.5):
        """
        size: (幅, 高さ)
        switch_interval: フレーム切り替えの間隔[秒]
        """
        self.frames = [
            cv2.imread("bird1.png", cv2.IMREAD_UNCHANGED),
            cv2.imread("bird2.png", cv2.IMREAD_UNCHANGED)
        ]
        if any(f is None for f in self.frames):
            raise FileNotFoundError("画像が見つかりません")
        
        self.frames = [cv2.resize(f, size) for f in self.frames]
        self.switch_interval = switch_interval
        self.last_switch = time.time()
        self.index = 0

    def get_frame(self, alive = True):
        now = time.time()
        if alive == False:
            return self.frames[self.index]
        if now - self.last_switch >= self.switch_interval:
            self.index = (self.index + 1) % len(self.frames)
            self.last_switch = now
        return self.frames[self.index]
    
def overlay_image_alpha(bg, fg, x, y):
    fg_h, fg_w = fg.shape[:2]
    bg_h, bg_w = bg.shape[:2]

    if x >= bg_w or y >= bg_h or x + fg_w <= 0 or y + fg_h <= 0:
        return bg
    
    x1 = max(x, 0)
    y1 = max(y, 0)
    x2 = min(x + fg_w, bg_w)
    y2 = min(y + fg_h, bg_h)

    fg_x1 = max(0, -x)
    fg_y1 = max(0, -y)
    fg_x2 = fg_x1 + (x2 - x1)
    fg_y2 = fg_y1 + (y2 - y1)

    fg_roi = fg[fg_y1:fg_y2, fg_x1:fg_x2]
    bg_roi = bg[y1:y2, x1:x2]

    if fg_roi.shape[0] == 0 or fg_roi.shape[1] == 0:
        return bg

    alpha = fg_roi[:, :, 3] / 255.0
    alpha = alpha[..., None]

    fg_rgb = fg_roi[:, :, :3]
    bg_roi[:] = (alpha * fg_rgb + (1 - alpha) * bg_roi).astype("uint8")

    return bg