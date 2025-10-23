# detector_facemesh.py
import cv2, numpy as np, mediapipe as mp
from dataclasses import dataclass
from typing import Tuple
from config import WIN_W, WIN_H, EAR_CLOSE_THRESH, EAR_OPEN_THRESH

MAR_OPEN_THRESH = 0.26

mp_mesh  = mp.solutions.face_mesh
mp_draw  = mp.solutions.drawing_utils
mp_style = mp.solutions.drawing_styles

R_EYE = [33, 160, 158, 133, 153, 144]
L_EYE = [263, 387, 385, 362, 380, 373]
MOUTH = [78, 13, 82, 14, 312, 308]

@dataclass
class MouthState:
    is_open: bool = False

@dataclass
class EyeState:
    is_closed: bool = False

def _dist(a, b): return float(np.linalg.norm(a - b))

def _ear_from_landmarks(pts, idxs):
    left, up1, up2, right, low1, low2= [pts[i] for i in idxs]
    horiz = _dist(left, right)
    vert  = (_dist(up1, low1) + _dist(up2, low2)) / 2.0
    return 0.0 if horiz < 1e-6 else vert / horiz

def _mar_from_landmarks(pts, idxs):
    left, up1, up2, low1, low2, right = [pts[i] for i in idxs]
    horiz = _dist(left, right)
    vert  = (_dist(up1, low1) + _dist(up2, low2)) / 2.0
    return 0.0 if horiz < 1e-6 else vert / horiz

class FaceInputDetector:
    def __init__(self, draw_mesh: bool = False):
        self.mouth = MouthState()
        self.eyes = EyeState()
        self.draw_mesh = draw_mesh
        self.mesh = mp_mesh.FaceMesh(
            max_num_faces=1, refine_landmarks=True,
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )

    def process(self, frame) -> Tuple[np.ndarray, bool, bool, float, float]:
        frame = cv2.resize(frame, (WIN_W, WIN_H))
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res  = self.mesh.process(rgb)

        mar, ear = 0.0, 0.0
        mouth_open = False
        eyes_closed = self.eyes.is_closed
        face_lms = None

        if res.multi_face_landmarks:
            face_lms = res.multi_face_landmarks[0]
            pts = np.array([(lm.x * w, lm.y * h) for lm in face_lms.landmark], dtype=np.float32)

            mar = _mar_from_landmarks(pts, MOUTH)
            mouth_open = mar > MAR_OPEN_THRESH

            ear_r = _ear_from_landmarks(pts, R_EYE)
            ear_l = _ear_from_landmarks(pts, L_EYE)
            ear = min(ear_r, ear_l)

            if not self.eyes.is_closed and ear < EAR_CLOSE_THRESH:
                self.eyes.is_closed = True
            elif self.eyes.is_closed and ear > EAR_OPEN_THRESH:
                self.eyes.is_closed = False

        if self.draw_mesh and face_lms is not None:
            mp_draw.draw_landmarks(
                frame, face_lms, mp_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_style.get_default_face_mesh_tesselation_style()
            )

        cv2.putText(frame, f"MAR:{mar:.2f} EAR:{ear:.2f}", (16, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2, cv2.LINE_AA)
        self.mouth.is_open = mouth_open
        return frame, mouth_open, eyes_closed, mar, ear

    def close(self): self.mesh.close()
