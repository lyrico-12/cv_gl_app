import cv2
import numpy as np
from config import WIN_W, WIN_H
from score_manager import update_best
import os


def _draw_centered_text(img, text, pos, scale, color, thickness=2):
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def show_game_over_menu(score: int, difficulty: str, window_name: str = "flappy bird advanced") -> str:
    """Show a simple menu allowing the player to Restart or Quit using the existing window.
    - window_name: the existing OpenCV window to render into (no new windows will be created).
    - base_vis: optional image (numpy array) to use as background; if provided it will be copied and used as backdrop.

    Returns: 'restart' or 'quit'
    """
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

    options = ["RESTART", "QUIT"]
    selected = 0

    # place the menu on the right side so it doesn't overlap the logo illustration
    menu_x = int(WIN_W * 0.75)

    while True:
        if logo is None:
            vis = 20 * np.ones((WIN_H, WIN_W, 3), dtype=np.uint8)
        else:
            vis = logo.copy()

        # title and score (draw on right-side menu area)
        _draw_centered_text(vis, "GAME OVER", (menu_x - 140, WIN_H//2 - 80), 1.4, (166,85,25), 3)
        _draw_centered_text(vis, f"Score: {score}", (menu_x - 80, WIN_H//2 - 30), 1.0, (255,255,255), 2)

        # draw options horizontally in the menu area
        for i, opt in enumerate(options):
            x = menu_x - 120
            y = WIN_H//2 + 30 + i * 60
            if i == selected:
                cv2.rectangle(vis, (x + 30, y-40), (x+180, y+20), (60,60,60), -1)
                if i == 1:
                    _draw_centered_text(vis, opt, (x+76, y), 0.9, (40,255,120), 2)
                else:
                    _draw_centered_text(vis, opt, (x+46, y), 0.9, (40,255,120), 2)
            else:
                if i == 1:
                    _draw_centered_text(vis, opt, (x+76, y), 0.9, (220,220,220), 2)
                else:
                    _draw_centered_text(vis, opt, (x+46, y), 0.9, (220,220,220), 2)


        # render into the provided window (do not create a new one)
        cv2.imshow(window_name, vis)
        key = cv2.waitKey(0) & 0xFF
        if key in [27, ord('q')]:
            choice = 1
        elif key in [82, ord('w')]:  # left arrow
            selected = (selected - 1) % len(options)
            continue
        elif key in [84, ord('s')]:  # right arrow
            selected = (selected + 1) % len(options)
            continue
        elif key in [13, 10, ord('\r')]:
            choice = selected
        else:
            continue


        if choice == 0:
            # restart requested
            return 'restart'

        # Quit chosen: update best and show comparison on same window
        prev_best = update_best(difficulty, score)
        best = max(prev_best, score)

        if logo is None:
            vis = 20 * np.ones((WIN_H, WIN_W, 3), dtype=np.uint8)
        else:
            vis = logo.copy()

        _draw_centered_text(vis, "RESULT", (menu_x - 60, WIN_H//2 - 110), 1.4, (166,85,25), 3)
        _draw_centered_text(vis, f"Your score: {score}", (menu_x - 90, WIN_H//2 - 40), 1.0, (255,255,255), 2)
        _draw_centered_text(vis, f"Best score ({difficulty}): {best}", (menu_x - 160, WIN_H//2 + 10), 1.0, (255,215,0), 2)
        _draw_centered_text(vis, "Press any key to exit", (menu_x - 80, WIN_H//2 + 80), 0.6, (180,180,180), 1)
        cv2.imshow(window_name, vis)
        cv2.waitKey(0)
        return 'quit'
