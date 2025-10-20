import cv2
import time
from detector_facemesh import FaceInputDetector, WIN_W, WIN_H

GRAVITY = 500.0
THRUST = 600.0
DT_CLAMP = 1/30
RADIUS = 18
PLAYER_X = int(WIN_W * 0.25)

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera open failed.")
        return 
    
    detector = FaceInputDetector(draw_mesh=False)
    y = WIN_H * 0.5
    vy = 0.0
    last_t = time.time()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            vis, mouth_open, mar = detector.process(frame)

            now = time.time()
            dt = min(now - last_t, DT_CLAMP)
            last_t = now

            ay = -THRUST if mouth_open else GRAVITY
            vy += ay * dt
            y += vy * dt

            if y < RADIUS:
                y = RADIUS
                vy = 0.0
            if y > WIN_H - RADIUS:
                y = WIN_H - RADIUS
                vy = 0.0

            cv2.circle(vis, (PLAYER_X, int(y)), RADIUS, (0, 170, 255), -1, cv2.LINE_AA)
            cv2.putText(vis, f"{'MOUTH OPEN' if mouth_open else 'mouth closed'} (MAR:{mar:.2f})",
                        (16, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 255, 0) if mouth_open else (160, 160, 160), 2, cv2.LINE_AA)
            cv2.putText(vis, "Q/Esc: quit  R: reset",
                        (16, WIN_H - 16), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            
            cv2.imshow("Mouthy Bird - proto", vis)

            key = cv2.waitKey(1) & 0xFF
            if key in [27, ord('q')]:
                break
            if key == ord('r'):
                y = WIN_H * 0.5
                vy = 0.0

    finally:
        detector.close()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()