import cv2
import numpy as np
import time
from dataclasses import dataclass
from typing import List, Tuple, Optional
import mediapipe as mp

WIN_W, WIN_H = 960, 540

EAR_CLOSE_THRESH = 0.40
EAR_OPEN_THRESH = 0.45

MAR_OPEN_THRESH = 0.26
MAR_CLOSE_THRESH = 0.20

mp_mesh = mp.solutions.face_mesh
mp_draw = mp.solutions.drawing_utils
mp_style = mp.solutions.drawing_styles

@dataclass
class BlinkState:
    is_closed: bool = False

@dataclass
class MouthState:
    is_open: bool = False

def open_camera() -> cv2.VideoCapture:
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIN_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WIN_H)
    if not cap.isOpened():
        raise RuntimeError("Camera open failed")
    return cap

R_EYE = [33, 160, 158, 133, 153, 144]
L_EYE = [263, 387, 385, 362, 380, 373]
MOUTH = [78, 13, 82, 14, 312, 308]

def dist(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))

def ear_from_landmarks(pts: np.ndarray, idxs: list) -> float:
    left, up1, up2, right, low1, low2 = [pts[i] for i in idxs]
    horiz = dist(left, right)
    vert = (dist(up1, low1) + dist(up2, low2)) / 2.0
    if horiz < 1e-6:
        return 0.0
    return vert / horiz

def mar_from_landmarks(pts: np.ndarray, idxs: list) -> float:
    left, up1, up2, low1, low2, right = [pts[i] for i in idxs]
    horiz = dist(left, right)
    vert = (dist(up1, low1) + dist(up2, low2)) / 2.0
    if horiz < 1e-6:
        return 0.0
    return vert / horiz

def update_blink_state_from_ear(ear: float, blink: BlinkState) -> bool:
    event = False
    if not blink.is_closed and ear < EAR_CLOSE_THRESH:
        blink.is_closed = True
        event = True
    
    elif blink.is_closed and ear > EAR_OPEN_THRESH:
        blink.is_closed = False
    return event

def update_mouth_state_from_mar(mar: float, mouth: MouthState) -> bool:
    """
    口が開いている間ずっと True を返す（連続出力）。
    ヒステリシスは使わない。
    """
    is_open_now = mar > MAR_OPEN_THRESH
    mouth.is_open = is_open_now  # 状態は更新だけしておく
    return is_open_now  

def draw_overlays(frame, ear, mar, face_landmarks=None, mesh=None):
    h, w = frame.shape[:2]
    if face_landmarks is not None and mesh is not None:
        mp_draw.draw_landmarks(
            frame, face_landmarks,
            mp_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_style.get_default_face_mesh_tesselation_style()
        )
    cv2.putText(frame, f"EAR:{ear:.2f}  MAR:{mar:.2f}", (16, 36),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2, cv2.LINE_AA)

def process_frame_facemesh(frame, mesh, blink: BlinkState, mouth: MouthState):
    """
    1フレーム：FaceMesh推論→EAR/MAR計算→イベント判定→可視化
    戻り値：(vis_frame, blink_event, mouth_event)
    """
    frame = cv2.resize(frame, (WIN_W, WIN_H))
    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
    rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    res = mesh.process(rgb)

    ear, mar = 0.0, 0.0
    blink_event = False
    mouth_event = False
    face_lms_draw = None

    if res.multi_face_landmarks:
        face = res.multi_face_landmarks[0]
        face_lms_draw = face  # 可視化用

        # (x,y) pixel座標配列を作る
        pts = np.array([(lm.x * w, lm.y * h) for lm in face.landmark], dtype=np.float32)

        # EAR（両目の平均）
        ear_r = ear_from_landmarks(pts, R_EYE)
        ear_l = ear_from_landmarks(pts, L_EYE)
        ear = (ear_r + ear_l) / 2.0

        # MAR（口）
        mar = mar_from_landmarks(pts, MOUTH)

        # イベント更新
        blink_event = update_blink_state_from_ear(ear, blink)
        mouth_event = update_mouth_state_from_mar(mar, mouth)

    draw_overlays(frame, ear, mar, face_lms_draw, mp_mesh)

    return frame, blink_event, mouth_event

def main():
    cap = open_camera()
    blink = BlinkState()
    mouth = MouthState()

    # FaceMesh 初期化
    with mp_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,           # 目・口まわりが精密
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as mesh:

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            vis, blink_event, mouth_event = process_frame_facemesh(frame, mesh, blink, mouth)

            # 標準出力イベント
            if blink_event:
                print(1, flush=True)   # 瞬き
            if mouth_event:
                print(2, flush=True)   # 口を開けた瞬間

            cv2.imshow("FaceMesh Blink & Mouth Detector", vis)
            key = cv2.waitKey(1) & 0xFF
            if key in [27, ord('q')]:
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()