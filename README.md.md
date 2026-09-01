# CEVI
## NB: For the moment the first version and the code itself is in French since I had not done the program to put it on github, so excuse and since the project is open source, you can easily adapt it to your language

Soon I will make the second version but in English, thank you for understanding
[![License: GNUv3](https://img.shields.io/badge/License-GNUv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

CEVI — Android-on-Linux toolbox: connect your phone over Wi-Fi (ADB), mirror
& record its screen with scrcpy + v4l2loopback, run diagnostics and install
dependencies with an explicit sudo password prompt. Plugin-based: drop a
Python file in `actions/` and it works in both CLI and PyQt6 GUI.

## Features

- **Screenshot & screen recording** of an Android phone directly from Linux
- **View Once capture** — save one-time photos/videos from WhatsApp & Facebook
- **Wireless connection** to your phone via ADB over Wi-Fi
- **Interactive GUI** (PyQt6) with auto-generated forms, live console output,
  and explicit sudo password prompts
- **Plugin system** — each action is a self-contained Python file, discovered
  automatically
- Works the same in **CLI** and **GUI** mode

## Requirements

- Linux (sudo rights required for installation and module loading)
- Python 3.8+
- Python packages: `pip install PyQt6`
- System tools: `adb`, `scrcpy`, `ffmpeg`, `v4l2loopback`
  (CEVI can install the missing ones for you — see the `installer_*` actions)

## Installation

```bash
python -m venv venv && source venv/bin/activate
git clone https://github.com/<your-username>/CEVI.git
cd CEVI && cd CEVI
pip install PyQt6
```

Connect your phone (USB debugging enabled) and pair it once with
`scrcpy` or `adb pair <phone-ip>:<port>` for wireless use.

## Usage

**Graphical mode:**

```bash
python main.py -mg
```

**List available actions:**

```bash
python main.py -l
```

**Run an action from the terminal:**

```bash
# Take a screenshot of the phone screen
python main.py -e capture_ecran

# Record the screen for 10 seconds
python main.py -e enregistrer_ecran --args duree=10

# Connect to the phone over Wi-Fi
python main.py -e connecter_telephone --args ip=192.168.1.24 port=5555
```

**Interactive menu** (same options as the original CEVI):

```bash
python main.py
```

When an action needs administrator rights (e.g. loading the `v4l2loopback`
module), CEVI **asks for your sudo password explicitly** — through a dialog
box in GUI mode, or hidden input in the terminal. The password is never
displayed or stored.

## How it works — capturing "View Once" media

CEVI captures one-time (View Once) photos from WhatsApp and Facebook by
mirroring the phone's screen onto the computer instead of taking a
screenshot on the device itself. The pipeline relies on three standard
Linux components:

1. **v4l2loopback** (kernel module) — creates a virtual camera device
   on your PC (`/dev/video2`).
2. **scrcpy** (headless mode) — streams the live screen of the connected
   Android phone straight into that virtual device:
   `scrcpy --no-window --v4l2-sink=/dev/video2`.
3. **ffmpeg** — reads back exactly one frame from the virtual camera and
   saves it as a timestamped PNG:
   `ffmpeg -i /dev/video2 -frames:v 1 <date>_<time>capture.png`.

Before capturing, CEVI checks which app is currently in the foreground
by reading `mCurrentFocus` from Android's `dumpsys window` output, and
only proceeds when WhatsApp or Facebook is displayed. You then simply
open the photo on the phone: while it is displayed once on the mirrored
screen, ffmpeg grabs the frame on the computer side.

Since the picture is taken from the virtual camera on the PC, the phone
never performs a screenshot itself — the capture happens entirely
outside the app.

For **View Once videos**, use the screen-recording action instead:
scrcpy records the mirrored stream to an MP4 file for a chosen duration
(then v4l2loopback is automatically unloaded).

## Available actions

| Action                       | Description                                       |
| ---------------------------- | ------------------------------------------------- |
| `capture_ecran`              | Screenshot of the phone screen (View Once photos) |
| `enregistrer_ecran`          | Screen recording as MP4 (View Once videos)        |
| `connecter_telephone`        | Connect the phone over Wi-Fi (ADB TCP/IP)         |
| `deconnecter_adb`            | Disconnect the ADB server                         |
| `diagnostic`                 | Check that everything is installed and reachable  |
| `lister_peripheriques_video` | List `/dev/video*` devices                        |
| `verifier_appli`             | Check which app is currently in the foreground    |
| `installer_headers`          | Install Linux headers (sudo)                      |
| `installer_ffmpeg`           | Install ffmpeg (sudo)                             |
| `installer_modprobe`         | Install modprobe/kmod (sudo)                      |
| `installer_v4l2loopback`     | Install v4l2loopback (sudo)                       |
| `lancer_v4l2loopback`        | Load the v4l2loopback module (sudo)               |

## Some screenshots
1. This is the field that allows you to set the recording time of the phone screen connected to the pc via adb
   But it uses in the background the v4l2loopback module contained in the linux kernel (it will be installed in auto if absent)

![[Capture d’écran du 2026-08-30 17-58-22.png|700]]

2. Here you will choose the number of the virtual device created by the v4l2loopback module (virtual camera) that will allow you to take screen recording and screen capture only on view

![[Capture d’écran du 2026-09-01 18-59-41.png]]

3. This is the interface that will allow you to set the IP and port on which your computer will connect to your phone via adb

![[Capture d’écran du 2026-09-01 19-07-40.png]]

4. The rest of the interface will allow you to **easily install the dependencies in order to have the v4l2loopback module available for transferring image streams from a window to ffmpeg**

![[Capture d’écran du 2026-09-01 19-10-40.png]]


## Add your own actions

CEVI is plugin-based: create a new `.py` file in the `actions/` folder,
register your function, and it instantly appears in the CLI list and in
the GUI — no other change needed.

```python
# actions/hello.py
from noyau.registre import enregistrer_action, Parametre

@enregistrer_action(
    "hello", "Say hello",
    "A minimal custom action.",
    parametres=[Parametre("nom", type="str", defaut="world")],
)
def hello(nom="world"):
    return f"Hello, {nom}!"
```

```bash
python main.py -e hello --args nom=CEVI
```

## Disclaimer ⚠️

This project is offered for educational and personal purposes.
Only media that you have the right to retain and respect the privacy of the persons with whom you communicate, as well as the terms and conditions of service of
the application involved.
Any attempts to use outside the permission area would be at your sole risk

## License

This project is licensed under the **GNU General Public License v3.0** —
see the [LICENSE](LICENSE) file for details.