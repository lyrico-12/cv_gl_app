# obstacles.py
import cv2
import random
from dataclasses import dataclass
from typing import List
from config import WIN_W, WIN_H, SCROLL_SPEED, PIPE_WIDTH, PIPE_GAP_H, PIPE_GAP_MIN_Y, PIPE_GAP_MAX_Y, PLAYER_X, RADIUS

def circle_rect_collision(cx, cy, r, rx, ry, rw, rh) -> bool:
    # 円とAxis-Aligned矩形の衝突
    nearest_x = max(rx, min(cx, rx + rw))
    nearest_y = max(ry, min(cy, ry + rh))
    dx = cx - nearest_x
    dy = cy - nearest_y
    return (dx*dx + dy*dy) <= (r*r)

@dataclass
class Pipe:
    x: float
    gap_y: float
    w: int = PIPE_WIDTH
    gap_h: int = PIPE_GAP_H
    passed: bool = False

    def update(self, dt: float):
        self.x -= SCROLL_SPEED * dt

    def offscreen(self) -> bool:
        return self.x + self.w < 0

    def draw(self, frame):
        # 上パイプ
        top_h = int(self.gap_y - self.gap_h/2)
        cv2.rectangle(frame, (int(self.x), 0), (int(self.x + self.w), top_h), (60, 180, 60), -1)
        # 下パイプ
        bot_y = int(self.gap_y + self.gap_h/2)
        cv2.rectangle(frame, (int(self.x), bot_y), (int(self.x + self.w), WIN_H), (60, 180, 60), -1)
        # ふち
        cv2.rectangle(frame, (int(self.x), 0), (int(self.x + self.w), top_h), (40,120,40), 3)
        cv2.rectangle(frame, (int(self.x), bot_y), (int(self.x + self.w), WIN_H), (40,120,40), 3)

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
