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

# === Eyes / Life gauge ===
EAR_CLOSE_THRESH = 0.38   # これ未満で「閉」
EAR_OPEN_THRESH  = 0.43  # これ超で「開」  ※ヒステリシス

LIFE_MAX          = 5           # ライフの上限
LIFE_GAUGE_RATE   = 0.35      # 目を閉じている間のゲージ充填速度 [ゲージ/秒]
LIFE_GAUGE_UNIT   = 1.0         # 満タン量（1.0で1回回復）
LIFE_GAUGE_COOLDOWN = 0.0       # 回復後のクールタイム(秒)。不要なら0

BIRD_IMG = {
    "EASY": ["assets/bird1.png", "assets/bird2.png"],
    "NORMAL": ["assets/bird3.png", "assets/bird4.png"],
    "HARD": ["assets/bird5.png", "assets/bird6.png"],
}

DIFFICULTY_PRESETS = {
    "EASY": {"gravity": 300.0,"thrust": 350.0,"scroll_speed": 180.0, "spawn_interval_min": 2.5, "spawn_interval_max": 3.5, "pipe_gap_h": 200, "life_gauge_rate": 0.5},
    "NORMAL": {"gravity": 500.0,"thrust": 600.0,"scroll_speed": 220.0, "spawn_interval_min": 2.0, "spawn_interval_max": 3.0, "pipe_gap_h": 170, "life_gauge_rate": 0.35},
    "HARD":{"gravity": 700.0,"thrust": 900.0,"scroll_speed": 260.0, "spawn_interval_min": 1.5, "spawn_interval_max": 2.5, "pipe_gap_h": 140, "life_gauge_rate": 0.2},
}