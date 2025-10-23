import cv2
from config import WIN_W, WIN_H
import numpy as np

def show_difficulty_menu() -> str:
    difficulties = ["EASY", "NORMAL", "HARD"]
    selected = difficulties.index("NORMAL")

    while True:
        vis = 255 * np.ones((WIN_H, WIN_W, 3), dtype=np.uint8)

        title = "FLAPPY BIRD ADVANCED"
        cv2.putText(vis, title, (WIN_W//2 - 180, WIN_H//2 - 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 2.0, (40,120,255), 6, cv2.LINE_AA)
        cv2.putText(vis, "Select Difficulty", (WIN_W//2 - 200, WIN_H//2 - 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200,200,200), 2, cv2.LINE_AA)

        for i, diff in enumerate(difficulties):
            color = (255,255,255)
            if i == selected:
                color = (40,255,120)
                cv2.rectangle(vis, (WIN_W//2 - 160, WIN_H//2 - 20 + i*60),
                              (WIN_W//2 + 160, WIN_H//2 + 20 + i*60),
                              (60,60,60), -1)
            cv2.putText(vis, diff, (WIN_W//2 - 60, WIN_H//2 + i*60 + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3, cv2.LINE_AA)

        cv2.putText(vis, "↑↓ to select, ENTER to start", (WIN_W//2 - 200, WIN_H - 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180,180,180), 2, cv2.LINE_AA)

        cv2.imshow(title, vis)
        key = cv2.waitKey(50) & 0xFF

        if key in [27, ord('q')]:
            cv2.destroyAllWindows()
            exit(0)
        elif key in [ord('w'), 82]:  # ↑キー or W
            selected = (selected - 1) % len(difficulties)
        elif key in [ord('s'), 84]:  # ↓キー or S
            selected = (selected + 1) % len(difficulties)
        elif key in [13, 10, ord('\r')]:  # Enterキー
            cv2.destroyAllWindows()
            return difficulties[selected]