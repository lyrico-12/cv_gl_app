import time
from dataclasses import dataclass
from config import LIFE_MAX, LIFE_GAUGE_RATE, LIFE_GAUGE_UNIT, LIFE_GAUGE_COOLDOWN, DIFFICULTY_PRESETS

@dataclass
class LifeGauge:
    """
    目を閉じている間 dt * LIFE_GAUGE_RATE だけゲージが増え、
    満タン(LIFE_GAUGE_UNIT)に達するたびにライフ+1（上限LIFE_MAX）。
    """
    value: float = 0.0
    cooldown_until: float = 0.0
    difficulty: str = "NORMAL"

    def update(self, eyes_closed: bool, dt: float, lives: int) -> int:
        """
        追加で増えたライフ数を返す
        """
        now = time.time()
        gained = 0
        life_gauge_rate = DIFFICULTY_PRESETS[self.difficulty]["life_gauge_rate"]

        if now < self.cooldown_until:
            return 0
        
        if eyes_closed:
            self.value += life_gauge_rate * dt
            while self.value >= LIFE_GAUGE_UNIT and lives + gained < LIFE_MAX:
                self.value -= LIFE_GAUGE_UNIT
                gained += 1
                if LIFE_GAUGE_COOLDOWN > 0:
                    self.cooldown_until = time.time() + LIFE_GAUGE_COOLDOWN
                    break
        
        else:
            pass

        return gained
    
    def fill_ratio(self) -> float:
        return max(0.0, min(1.0, self.value / LIFE_GAUGE_UNIT))