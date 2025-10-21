# config.py
WIN_W, WIN_H = 960, 540

# 物理
GRAVITY = 500.0     # 下向き加速度 [px/s^2]
THRUST  = 600.0     # 口開き中の上向き加速度 [px/s^2]
DT_CLAMP = 1/30.0
RADIUS  = 25
PLAYER_X = int(WIN_W * 0.25)

# スクロール/障害物
SCROLL_SPEED = 220.0  # 地面/障害物の左方向速度 [px/s]
SPAWN_INTERVAL = 1.6  # パイプ出現間隔 [s]
PIPE_WIDTH = 90
PIPE_GAP_H = 170      # ギャップ高さ [px]
PIPE_GAP_MIN_Y = 140  # 画面上からギャップ中心がこの下より
PIPE_GAP_MAX_Y = WIN_H - 140

INVINCIBLE_S = 1.0
HIT_KNOCKBACK_VY = -600