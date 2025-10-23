# mouthy_bird_game.py
import cv2, time
from config import *
from detector_facemesh import FaceInputDetector
from obstacles import spawn_pipe, update_pipes, check_score_and_collision
from bird_anim import BirdAnimator, overlay_image_alpha
from life_gauge import LifeGauge

def draw_life_gauge(vis, ratio: float, lives: int):
    x, y, w, h = 16, 100, 180, 14
    cv2.rectangle(vis, (x, y), (x+w, y+h), (60, 60, 60), 2, cv2.LINE_AA)
    fill_w = int(w * max(0.0, min(1.0, ratio)))
    cv2.rectangle(vis, (x+1, y+1), (x+1+fill_w, y+h-1), (90, 230, 90), -1, cv2.LINE_AA)
    cv2.putText(vis, f"Lives: {lives}", (x, y-8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(vis, "Heal", (x+w+8, y+h-2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 255, 180), 1, cv2.LINE_AA)

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera open failed.")
        return

    detector = FaceInputDetector(draw_mesh=False)
    bird = BirdAnimator()
    life_gauge = LifeGauge()

    y = WIN_H * 0.5
    vy = 0.0
    pipes = []
    time_from_spawn = 0.0
    score = 0
    lives = 3
    invincible_until = 0.0
    last_t = time.time()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            vis, mouth_open, eyes_closed, mar, ear = detector.process(frame)

            now = time.time()
            dt = min(now - last_t, DT_CLAMP)
            last_t = now
            is_invincible = now < invincible_until

            if lives > 0:
                # 物理更新
                ay = -THRUST if mouth_open else GRAVITY
                vy += ay * dt
                y  += vy * dt

                # 画面端で止める
                if y < RADIUS:
                    y, vy = RADIUS, 0.0
                if y > WIN_H - RADIUS:
                    y, vy = WIN_H - RADIUS, 0.0

                # パイプ生成・更新
                time_from_spawn += dt
                if time_from_spawn >= SPAWN_INTERVAL:
                    time_from_spawn = 0.0
                    pipes.append(spawn_pipe(WIN_W + 20))

                pipes = update_pipes(pipes, dt)
                for p in pipes:
                    p.draw(vis)

                # スコア・衝突判定
                inc, hit = check_score_and_collision(pipes, PLAYER_X, int(y))
                score += inc
                if hit and not is_invincible:
                    lives -= 1
                    invincible_until = now + INVINCIBLE_S

                gained = life_gauge.update(eyes_closed=eyes_closed, dt=dt, lives=lives)
                if gained > 0:
                    lives = min(LIFE_MAX, lives + gained)

            else:
                # ゲームオーバー表示
                cv2.putText(vis, "GAME OVER", (WIN_W//2 - 150, WIN_H//2 - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (40,40,255), 3, cv2.LINE_AA)
                cv2.putText(vis, "Press R to restart", (WIN_W//2 - 170, WIN_H//2 + 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2, cv2.LINE_AA)
                for p in pipes:
                    p.draw(vis)

            # if now < invincible_until and lives > 0:
            #     flicker = int(now * 10) % 2 ==0
            #     color = (0, 170, 255) if flicker else (180, 180, 180)
            # else:
            #     color = (0, 170, 255)

            # # プレイヤー描画
            # cv2.circle(vis, (PLAYER_X, int(y)), RADIUS, color, -1, cv2.LINE_AA)

            flicker_on = True

            if is_invincible and lives > 0:
                flicker_on = (int(now * 10) % 2 ==0)

            if flicker_on:
                bird_img = bird.get_frame() if lives > 0 else bird.get_frame(alive=False)
                x = PLAYER_X - bird_img.shape[1] // 2 - 20
                y_top = int(y) - bird_img.shape[0] // 2 - 20
                vis = overlay_image_alpha(vis, bird_img, x, y_top)

            # スコア
            cv2.putText(vis, f"Score: {score}", (16, 36),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)
            draw_life_gauge(vis, life_gauge.fill_ratio(), lives)
            
            if is_invincible and lives > 0:
                cv2.putText(vis, f"Invincible: {invincible_until - now:.1f}s",
                            (16, 132), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (80, 220, 255), 2)

            cv2.imshow("Mouthy Bird", vis)

            # キー操作
            key = cv2.waitKey(1) & 0xFF
            if key in [27, ord('q')]:
                break
            if key == ord('r'):
                y = WIN_H * 0.5
                vy = 0.0
                pipes.clear()
                time_from_spawn = 0.0
                score = 0
                lives = 3
                invincible_until = 0.0

    finally:
        detector.close()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
