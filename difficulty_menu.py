import os
import cv2
from config import WIN_W, WIN_H
import numpy as np

def show_difficulty_menu() -> str:
    difficulties = ["EASY", "NORMAL", "HARD"]
    selected = difficulties.index("NORMAL")

    # try to load logo once
    logo = None
    # prefer PNG but fall back to JPG if present
    logo_path_png = os.path.join("assets", "logo.png")
    logo_path_jpg = os.path.join("assets", "logo.jpg")
    logo_path = logo_path_png if os.path.exists(logo_path_png) else (logo_path_jpg if os.path.exists(logo_path_jpg) else None)
    if logo_path is not None:
        logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
        if logo is not None:
            try:
                # resize logo to window size (may contain alpha channel)
                logo = cv2.resize(logo, (WIN_W, WIN_H), interpolation=cv2.INTER_AREA)
            except Exception:
                # keep logo as-is if resize fails
                pass

    while True:
        # create base visual either from logo (with alpha blending) or white background
        if logo is None:
            vis = 255 * np.ones((WIN_H, WIN_W, 3), dtype=np.uint8)
        else:
            # logo may have 3 (BGR) or 4 (BGRA) channels
            if logo.ndim == 3 and logo.shape[2] == 4:
                bgr = logo[:, :, :3].astype(np.float32)
                alpha = (logo[:, :, 3].astype(np.float32) / 255.0)
                alpha_stack = np.dstack([alpha, alpha, alpha])
                base = 255 * np.ones((WIN_H, WIN_W, 3), dtype=np.float32)
                vis = (bgr * alpha_stack + base * (1.0 - alpha_stack)).astype(np.uint8)
            else:
                # no alpha, just copy (ensure 3 channels)
                vis = logo.copy()

        # layout menu on the right side so it doesn't overlap the logo illustration
        menu_x = int(WIN_W * 0.75)
        # title near the top of the menu area
        cv2.putText(vis, "Select Difficulty", (menu_x - 120, WIN_H//2 - 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200,200,200), 2, cv2.LINE_AA)

        # draw a semi-transparent selection rectangle behind the selected difficulty
        overlay = vis.copy()
        rect_tl = (menu_x - 160, WIN_H//2 - 20 + selected*60)
        rect_br = (menu_x + 130, WIN_H//2 + 20 + selected*60)
        cv2.rectangle(overlay, rect_tl, rect_br, (60, 60, 60), -1)
        vis = cv2.addWeighted(overlay, 0.6, vis, 0.4, 0)

        for i, diff in enumerate(difficulties):
            color = (255, 255, 255)
            if i == selected:
                color = (166, 85, 25)
            if i == 1:
                cv2.putText(vis, diff, (menu_x - 80, WIN_H//2 + i*60 + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3, cv2.LINE_AA)
            else:
                cv2.putText(vis, diff, (menu_x - 60, WIN_H//2 + i*60 + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3, cv2.LINE_AA)

        cv2.imshow("FLAPPY BIRD ADVANCED", vis)
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