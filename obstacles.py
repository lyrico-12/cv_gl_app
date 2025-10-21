# obstacles.py
import cv2
import random
from dataclasses import dataclass, field
from typing import List
from config import WIN_W, WIN_H, SCROLL_SPEED, PIPE_WIDTH, PIPE_GAP_H, PIPE_GAP_MIN_Y, PIPE_GAP_MAX_Y, PLAYER_X, RADIUS

def circle_rect_collision(cx, cy, r, rx, ry, rw, rh) -> bool:
    # 円とAxis-Aligned矩形の衝突
    nearest_x = max(rx, min(cx, rx + rw))
    nearest_y = max(ry, min(cy, ry + rh))
    dx = cx - nearest_x
    dy = cy - nearest_y
    return (dx*dx + dy*dy) <= (r*r)


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))

def _shift_color(bgr, db=0, dg=0, dr=0):
    # BGR各チャンネルをシフトしてクリップ
    b, g, r = bgr
    return (_clamp(b+db, 0, 255), _clamp(g+dg, 0, 255), _clamp(r+dr, 0, 255))

def _draw_vertical_cylinder(frame, x, y0, y1, w, base, outline, line_aa=cv2.LINE_AA):
    """
    y0〜y1の縦パイプ胴体を描く（円筒っぽい2トーン＋ハイライト帯＋外周線）
    """
    x0, x1 = int(x), int(x + w)
    y0, y1 = int(y0), int(y1)
    if y1 <= y0: 
        return

    # 胴体ベース
    cv2.rectangle(frame, (x0, y0), (x1, y1), base, -1)

    # 右側を少し暗めにして円筒陰影
    dark = _shift_color(base, db=-20, dg=-40, dr=-20)
    cv2.rectangle(frame, (x0 + int(w*0.65), y0), (x1, y1), dark, -1)

    # 左側に細いハイライト帯
    light = _shift_color(base, db=+30, dg=+55, dr=+30)
    hl_x0 = x0 + int(w*0.08)
    hl_x1 = x0 + int(w*0.16)
    cv2.rectangle(frame, (hl_x0, y0), (hl_x1, y1), light, -1)

    # 外周アウトライン
    cv2.rectangle(frame, (x0, y0), (x1, y1), outline, 2, lineType=line_aa)

@dataclass
class Pipe:
    x: float
    gap_y: float
    w: int = PIPE_WIDTH
    gap_h: int = PIPE_GAP_H
    passed: bool = False

    # 見た目の個体差（明度少しランダム）
    def _colors(self):
        base = (60, 180, 60)    # BGR
        outline = (40, 120, 40)
        jitter = 0
        base = _shift_color(base, dg=jitter, db=jitter//2, dr=jitter//3)
        return base, outline

    def update(self, dt: float):
        self.x -= SCROLL_SPEED * dt

    def offscreen(self) -> bool:
        return self.x + self.w < 0

    def draw(self, frame):
        base, outline = self._colors()
        top_h = int(self.gap_y - self.gap_h/2)
        bot_y = int(self.gap_y + self.gap_h/2)

        # --- 上パイプ（上からギャップまで） ---
        if top_h > 0:
            _draw_vertical_cylinder(frame, self.x, 0, top_h, self.w, base, outline)

        # --- 下パイプ（ギャップから下端まで） ---
        if bot_y < WIN_H:
            _draw_vertical_cylinder(frame, self.x, bot_y, WIN_H, self.w, base, outline)

    def collide_circle(self, cx: int, cy: int, r: int) -> bool:
        top_rect = (int(self.x), 0, self.w, int(self.gap_y - self.gap_h/2))
        bot_rect = (int(self.x), int(self.gap_y + self.gap_h/2), self.w, WIN_H - int(self.gap_y + self.gap_h/2))
        (rx, ry, rw, rh) = top_rect
        if rh > 0 and circle_rect_collision(cx, cy, r, rx, ry, rw, rh): return True
        (rx, ry, rw, rh) = bot_rect
        if rh > 0 and circle_rect_collision(cx, cy, r, rx, ry, rw, rh): return True
        return False

def spawn_pipe(x: float) -> Pipe:
    gy = random.randint(PIPE_GAP_MIN_Y, PIPE_GAP_MAX_Y)
    return Pipe(x=float(x), gap_y=float(gy))

def update_pipes(pipes: List[Pipe], dt: float):
    for p in pipes: p.update(dt)
    return [p for p in pipes if not p.offscreen()]

def check_score_and_collision(pipes: List[Pipe], cx: int, cy: int):
    score_inc = 0
    hit = False
    for p in pipes:
        if p.collide_circle(cx, cy, RADIUS): hit = True
        if not p.passed and (p.x + p.w) < cx:
            p.passed = True
            score_inc += 1
    return score_inc, hit
