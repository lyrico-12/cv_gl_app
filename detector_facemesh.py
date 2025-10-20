# detector_facemesh.py
import cv2
import numpy as np
import mediapipe as mp
from dataclasses import dataclass
from typing import Optional, Tuple

WIN_W, WIN_H = 960, 540

# 口（MAR）しきい値
MAR_OPEN_THRESH  = 0.26

mp_mesh  = mp.solutions.face_mesh
mp_draw  = mp.solutions.drawing_utils
mp_style = mp.solutions.drawing_styles

# ランドマーク index
R_EYE = [33, 160, 158, 133, 153, 144]
L_EYE = [263, 387, 385, 362, 380, 373]
MOUTH = [78, 13, 82, 14, 312, 308]

@dataclass
class MouthState:
    is_open: bool = False

def _dist(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))

def _mar_from_landmarks(pts: np.ndarray, idxs: list) -> float:
    left, up1, up2, low1, low2, right = [pts[i] for i in idxs]
    horiz = _dist(left, right)
    vert  = (_dist(up1, low1) + _dist(up2, low2)) / 2.0
    return 0.0 if horiz < 1e-6 else vert / horiz

class FaceInputDetector:
    """MediaPipe FaceMeshで口の開きを検出する小さなユーティリティ"""
    def __init__(self, draw_mesh: bool = True):
        self.mouth = MouthState()
        self.draw_mesh = draw_mesh
        self.mesh = mp_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def process(self, frame) -> Tuple[np.ndarray, bool, float]:
        """
        1フレーム処理
        Returns: (可視化済みフレーム, mouth_open(bool), mar(float))
        """
        frame = cv2.resize(frame, (WIN_W, WIN_H))
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        res = self.mesh.process(rgb)

        mar = 0.0
        mouth_open = False
        face_lms_draw = None

        if res.multi_face_landmarks:
            face = res.multi_face_landmarks[0]
            face_lms_draw = face
            pts = np.array([(lm.x * w, lm.y * h) for lm in face.landmark], dtype=np.float32)
            mar = _mar_from_landmarks(pts, MOUTH)
            mouth_open = mar > MAR_OPEN_THRESH

        # 可視化（必要なければ mesh 描画を切る）
        if self.draw_mesh and face_lms_draw is not None:
            mp_draw.draw_landmarks(
                frame, face_lms_draw,
                mp_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_style.get_default_face_mesh_tesselation_style()
            )
        cv2.putText(frame, f"MAR:{mar:.2f}  (open>{MAR_OPEN_THRESH})",
                    (16, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2, cv2.LINE_AA)

        # 状態を更新して返す（開いている間はTrueのまま）
        self.mouth.is_open = mouth_open
        return frame, mouth_open, mar

    def close(self):
        self.mesh.close()
