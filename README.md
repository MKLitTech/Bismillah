# Bismillah Tracker 🕌

A webcam app that detects when you're eating and reminds you to say Bismillah before your meal. Made as a quick concept project — no AI, no internet connection required, runs fully offline.

> **Note:** This is a proof-of-concept, not a polished app. It has bugs (see below) and was built for fun. Built with the help of Claude (Anthropic).

<img width="640" height="480" alt="UI Preview" src="https://github.com/user-attachments/assets/80639c4f-59dc-4bf6-aa9f-84e3f69a4814" />

<img width="1053" height="642" alt="Eating Detected" src="https://github.com/user-attachments/assets/7688e813-1723-47ee-8a29-b91894670765" />

---

## How it works

It uses your webcam and Google's MediaPipe to track your face and hands in real time. When it detects your hand near your mouth for long enough, a popup appears on every monitor reminding you to say Bismillah. It also pauses any media you have playing (YouTube, Spotify, etc.) so you actually see it.

No data is sent anywhere. Everything runs locally on your machine.

---

## Requirements

- Windows 11
- A webcam

---

## Setup (fresh Windows install, start here)

**1. Install Python**

Go to [python.org/downloads](https://www.python.org/downloads/) and download the latest Python 3.x installer.

Run it, and on the first screen **make sure to check "Add Python to PATH"** before clicking Install. This is important — if you skip it, commands won't work.

<img width="672" height="417" alt="0_7nOyowsPsGI19pZT" src="https://github.com/user-attachments/assets/2138350e-6580-47ee-9574-9283297e2422" />

To verify it worked, open PowerShell (search for it in the Start menu) and run:
```
python --version
```
You should see something like `Python 3.12.x`.

**2. Download the project**

If you have Git installed:
```
git clone https://github.com/mklittech/bismillah
cd bismillah
```

Or just download the ZIP from the green **Code** button on this page, extract it, and open PowerShell inside that folder. (You can do this by navigating to the folder in File Explorer, then typing `powershell` in the address bar and pressing Enter.)

<img width="876" height="330" alt="image" src="https://github.com/user-attachments/assets/948a2903-4b2f-4152-acac-a090e99a5d0a" />


**3. Install dependencies**

In PowerShell, run:
```
pip install mediapipe opencv-python screeninfo
```

This will take a minute or two. You should see it downloading and installing packages.

**4. Run it**
```
python bismillah_tracker.py
```

The app will automatically download the two model files it needs on first run (~30MB total). A settings window will open — adjust the values if you want, then hit **Start**. The webcam window will open and it'll start tracking.

Press **Q** to quit.

> **If the script just freezes after running the command** — restart your PC and try again. This seems to be a driver or Python process issue on some machines and a reboot fixes it.

---

## Settings explained

| Setting | Default | What it does |
|---|---|---|
| Cooldown | 30:00 | How long to wait before alerting again after a confirmed eating detection |
| Sensitivity | 0.22 | How close your hand needs to be to your mouth to trigger (lower = stricter) |
| Detection frames | 6 | How many consecutive frames needed before triggering the popup |

---

## Known bugs

- **Freezes on first run** — if the app hangs after running the command, restart your PC and try again. A reboot fixes it.
- **False positives** — scratching your nose, gesturing, or resting your hand near your face can trigger it. That's why there's an "I wasn't eating" button on the popup — pressing it dismisses the alert without starting the cooldown.
- **Profile angle** — detection gets unreliable if you're sitting at a sharp angle to the camera. Works best face-on.
- **Single webcam only** — if you have multiple cameras it always picks the default one.
- **Windows only** — the media pause and popup features use Windows-specific APIs. It won't run on Mac, Linux, or Windows 10 without rewriting those parts.
- **Utensil detection is limited** — it tracks hand position, not whether you're actually holding a fork or spoon. Works okay in practice but isn't foolproof.

---

## Built with

- [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/guide) — hand and face landmark detection
- [OpenCV](https://opencv.org/) — webcam feed and overlays
- [tkinter](https://docs.python.org/3/library/tkinter.html) — settings and popup windows
- [Claude](https://claude.ai) by Anthropic — helped write and debug most of the code

---

## Support

Expect little to no support — this is a project I made for fun and do not actively maintain. Feel free to open an issue or fork it and fix it yourself, but I make no promises on response time.

---

## License

MIT — do whatever you want with it, just give me some credit.
