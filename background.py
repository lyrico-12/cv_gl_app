# background.py
import cv2
import numpy as np
from config import WIN_W, WIN_H, SCROLL_SPEED

class GroundScroller:
    """
    画面下にストライプ模様の床を描き、左に流す。
    """
    def __init__(self, height: int = 90, stripe_w: int = 40, alpha: float = 0.7):
        self.height = height
        self.stripe_w = stripe_w
        self.offset = 0.0
        self.alpha = alpha
        # 色
        self.c1 = (60, 60, 60)
        self.c2 = (90, 90, 90)

    def update(self, dt: float):
        self.offset = (self.offset + SCROLL_SPEED * dt) % self.stripe_w

    def draw(self, frame):
        y1 = WIN_H - self.height
        overlay = frame.copy()
        start_x = -int(self.offset)
        for i, x in enumerate(range(start_x, WIN_W + self.stripe_w, self.stripe_w)):
            color = self.c1 if (i % 2 == 0) else self.c2
            cv2.rectangle(overlay, (x, y1), (x + self.stripe_w - 6, WIN_H), color, -1)
        cv2.addWeighted(overlay, self.alpha, frame, 1 - self.alpha, 0, dst=frame)
        # 境界線
        cv2.line(frame, (0, y1), (WIN_W, y1), (120, 120, 120), 2, cv2.LINE_AA)
