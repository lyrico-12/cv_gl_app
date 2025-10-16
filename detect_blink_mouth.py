import cv2
import numpy as np
import time
from dataclasses import dataclass
from typing import List, Tuple, Optional

WIN_W, WIN_H = 960, 540

BLINK_ABSENT_MIN_MS = 40
BLINK_ABSENT_MAX_MS = 300
BLINK_REFRACTORY_S = 0.6

