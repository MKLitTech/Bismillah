import cv2
import mediapipe as mp
import time
import tkinter as tk
import sys
import ctypes
import os
import urllib.request
from screeninfo import get_monitors


# ── Media control ─────────────────────────────────────────────────────────────

def pause_media():
    VK_MEDIA_PLAY_PAUSE = 0xB3
    ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
    ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 2, 0)


# ── Settings window ───────────────────────────────────────────────────────────

class Settings:
    def __init__(self):
        self.cooldown_secs = 1800
        self.sensitivity   = 0.22
        self.frames_needed = 6
        self.confirmed     = False

    def show(self):
        root = tk.Tk()
        root.title("Bismillah Tracker — Settings")
        root.geometry("300x290")
        root.resizable(False, False)
        root.attributes("-topmost", True)

        fields = {}
        for label, key, default in [
            ("Cooldown (M:S, e.g. 30:00)", "cooldown", "30:00"),
            ("Sensitivity (0.1 – 0.3)",    "sens",     "0.22"),
            ("Detection frames",            "frames",   "6"),
        ]:
            tk.Label(root, text=label).pack(pady=(10, 0))
            e = tk.Entry(root)
            e.insert(0, default)
            e.pack()
            fields[key] = e

        def start():
            raw = fields["cooldown"].get()
            if ":" in raw:
                m, s = map(int, raw.split(":"))
                self.cooldown_secs = m * 60 + s
            else:
                self.cooldown_secs = int(raw)
            self.sensitivity   = float(fields["sens"].get())
            self.frames_needed = int(fields["frames"].get())
            self.confirmed     = True
            root.destroy()

        tk.Button(root, text="Start", command=start, bg="#2d6a4f", fg="white",
                  width=16, pady=6).pack(pady=20)
        root.mainloop()


# ── Reminder popup ────────────────────────────────────────────────────────────

def show_popup():
    pause_media()
    result = {"eating": False}
    root = tk.Tk()
    root.withdraw()

    def confirm():
        result["eating"] = True
        root.destroy()

    def false_positive():
        result["eating"] = False
        root.destroy()

    for monitor in get_monitors():
        win = tk.Toplevel(root)
        win.title("Bismillah Tracker")
        win.attributes("-topmost", True)
        win.resizable(False, False)
        w, h = 380, 165
        x = int(monitor.x + (monitor.width  - w) / 2)
        y = int(monitor.y + (monitor.height - h) / 2)
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.configure(bg="#f5f5f5")

        tk.Label(win, text="Remember to say Bismillah!",
                 font=("Segoe UI", 13, "bold"), bg="#f5f5f5", pady=22).pack()

        btns = tk.Frame(win, bg="#f5f5f5")
        btns.pack()
        tk.Button(btns, text="OK ✓",           width=11, command=confirm,
                  relief="groove", bg="#2d6a4f", fg="white").pack(side="left", padx=6)
        tk.Button(btns, text="I wasn't eating", width=14, command=false_positive,
                  relief="groove", bg="#e0a000", fg="white").pack(side="left", padx=6)
        tk.Button(btns, text="Quit",            width=8,  command=sys.exit,
                  relief="groove", bg="#cc3333", fg="white").pack(side="left", padx=6)

    root.mainloop()
    return result["eating"]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("step 1: opening settings...")
    cfg = Settings()
    cfg.show()
    print("step 2: settings done")
    if not cfg.confirmed:
        sys.exit()

    print("step 3: downloading models if needed...")
    models = {
        "hand_landmarker.task": "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        "face_landmarker.task": "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
    }
    for filename, url in models.items():
        if not os.path.exists(filename):
            print(f"  Downloading {filename}...")
            urllib.request.urlretrieve(url, filename)
            print(f"  Done.")
        else:
            print(f"  {filename} already exists, skipping.")

    print("step 4: loading mediapipe models...")
    BaseOptions = mp.tasks.BaseOptions
    VIDEO       = mp.tasks.vision.RunningMode.VIDEO

    hand_detector = mp.tasks.vision.HandLandmarker.create_from_options(
        mp.tasks.vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
            running_mode=VIDEO,
            num_hands=2,
        )
    )
    face_detector = mp.tasks.vision.FaceLandmarker.create_from_options(
        mp.tasks.vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path="face_landmarker.task"),
            running_mode=VIDEO,
        )
    )

    print("step 5: opening webcam...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam.")
        sys.exit()

    print("step 6: running! press Q to quit.")
    eating_frames = 0
    last_alert    = 0
    frame_i       = 0

    with hand_detector as h_det, face_detector as f_det:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_i += 1
            if frame_i % 5 != 0:
                time.sleep(0.01)
                continue

            frame     = cv2.flip(frame, 1)
            fh, fw, _ = frame.shape
            small     = cv2.resize(frame, (640, 480))
            mp_img    = mp.Image(image_format=mp.ImageFormat.SRGB,
                                 data=cv2.cvtColor(small, cv2.COLOR_BGR2RGB))
            ts        = int(time.time() * 1000)

            h_res = h_det.detect_for_video(mp_img, ts)
            f_res = f_det.detect_for_video(mp_img, ts)

            mouth   = None
            is_near = False

            if f_res.face_landmarks:
                lms    = f_res.face_landmarks[0]
                xs     = [lm.x for lm in lms]
                ys     = [lm.y for lm in lms]
                x1, x2 = min(xs), max(xs)
                y1, y2 = min(ys), max(ys)

                cv2.rectangle(frame,
                              (int(x1 * fw), int(y1 * fh)),
                              (int(x2 * fw), int(y2 * fh)),
                              (255, 100, 0), 2)
                cv2.putText(frame, "Face",
                            (int(x1 * fw), int(y1 * fh) - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 0), 1)

                mx    = (x1 + x2) / 2
                my    = y2 - (y2 - y1) * 0.2
                mouth = (mx, my)
                cv2.circle(frame, (int(mx * fw), int(my * fh)), 7, (0, 255, 0), -1)
                cv2.putText(frame, "Mouth",
                            (int(mx * fw) + 9, int(my * fh) + 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

            if h_res.hand_landmarks:
                for hand in h_res.hand_landmarks:
                    hxs = [lm.x for lm in hand]
                    hys = [lm.y for lm in hand]
                    hx1 = int(min(hxs) * fw)
                    hx2 = int(max(hxs) * fw)
                    hy1 = int(min(hys) * fh)
                    hy2 = int(max(hys) * fh)

                    near = False
                    if mouth:
                        for idx in [4, 8, 12]:
                            tip  = hand[idx]
                            dist = ((tip.x - mouth[0]) ** 2 + (tip.y - mouth[1]) ** 2) ** 0.5
                            if dist < cfg.sensitivity:
                                near    = True
                                is_near = True
                                break

                    color = (0, 0, 255) if near else (0, 200, 255)
                    label = "Hand (near mouth)" if near else "Hand"
                    cv2.rectangle(frame, (hx1, hy1), (hx2, hy2), color, 2)
                    cv2.putText(frame, label, (hx1, hy1 - 6),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            if is_near:
                eating_frames += 1
            else:
                eating_frames = max(0, eating_frames - 1)

            now    = time.time()
            eating = eating_frames >= cfg.frames_needed

            s_col = (0, 0, 255) if eating else (0, 200, 100)
            cv2.putText(frame, "EATING DETECTED" if eating else "Not eating",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, s_col, 2)
            cv2.putText(frame, "Press Q to quit",
                        (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (160, 160, 160), 1)

            if last_alert > 0 and (now - last_alert) < cfg.cooldown_secs:
                secs_left  = int(cfg.cooldown_secs - (now - last_alert))
                mins, secs = divmod(secs_left, 60)
                cv2.putText(frame, f"Cooldown: {mins}m {secs}s",
                            (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 100, 255), 1)

            fill = int(min(eating_frames / cfg.frames_needed, 1.0) * 200)
            cv2.rectangle(frame, (10, fh - 40), (210, fh - 20), (50, 50, 50), -1)
            cv2.rectangle(frame, (10, fh - 40), (10 + fill, fh - 20), (0, 200, 255), -1)
            cv2.putText(frame, "Confidence",
                        (10, fh - 44), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

            if eating and (now - last_alert) > cfg.cooldown_secs:
                was_eating    = show_popup()
                eating_frames = 0
                if was_eating:
                    last_alert = time.time()

            cv2.imshow("Bismillah Tracker", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()