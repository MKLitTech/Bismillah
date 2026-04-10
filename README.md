# Bismillah Tracker 🕌

A webcam app that detects when you're eating and reminds you to say Bismillah before your meal. Made as a quick concept project — no AI, no internet connection required, runs fully offline.

> **Note:** This is a proof-of-concept, not a polished app. It has bugs (see below) and was built for fun. Built with the help of Claude (Anthropic).

---

## How it works

It uses your webcam and Google's MediaPipe to track your face and hands in real time. When it detects your hand near your mouth for long enough, a popup appears on every monitor reminding you to say Bismillah. It also pauses any media you have playing (YouTube, Spotify, etc.) so you actually see it.

No data is sent anywhere. Everything runs locally on your machine.

---

## Requirements

- Windows 10 or 11
- Python 3.10+
- A webcam

---

## Setup

**1. Clone the repo**
```
git clone https://github.com/mklittech/bismillah
cd bismillah-tracker
```

**2. Install dependencies**
```
pip install mediapipe opencv-python screeninfo winrt-runtime tkinter
```

**3. Download the MediaPipe model files**

The app will download them automatically on first run, but if you want to grab them manually:
- [hand_landmarker.task](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task)
- [face_landmarker.task](https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task)

Place both files in the same folder as `bismillah_tracker.py`.

**4. Run it**
```
python bismillah_tracker.py
```

A settings window will open first where you can adjust the cooldown, sensitivity, and detection speed. Hit **Start** and the webcam window will open.

Press **Q** to quit.

---

## Settings explained

| Setting | Default | What it does |
|---|---|---|
| Cooldown | 30:00 | How long to wait before alerting again after a confirmed eating detection |
| Sensitivity | 0.22 | How close your hand needs to be to your mouth to trigger (lower = stricter) |
| Detection frames | 6 | How many consecutive frames needed before triggering the popup |

---

## Known bugs

- **False positives** — if you rest your hand on your face, scratch your nose, or gesture near your mouth, it can trigger. That's why there's an "I wasn't eating" button on the popup to skip the cooldown.
- **Profile angle** — detection is less reliable if you're sitting at a sharp angle to the camera.
- **Single webcam only** — if you have multiple cameras, it always picks the default one.
- **Windows only** — the media pause and popup features rely on Windows APIs. It won't run on Mac or Linux without changes.
- **Utensil detection is limited** — it detects hand position, not whether you're actually holding a fork or spoon. It works okay in practice but isn't perfect.

---

## Built with

- [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/guide) — hand and face landmark detection
- [OpenCV](https://opencv.org/) — webcam feed and overlays
- [winrt](https://github.com/pywinrt/pywinrt) — Windows media session control
- [tkinter](https://docs.python.org/3/library/tkinter.html) — settings and popup windows
- [Claude](https://claude.ai) by Anthropic — helped write and debug most of the code

---

## License

MIT — do whatever you want with it.
