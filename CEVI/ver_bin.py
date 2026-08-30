import shutil

def verfi_ffmpeg():
    try:
        if shutil.which("ffmpeg"):
            return "ffmpeg présent"
        else:
            return "ffmpeg absent"
    except (TypeError, ValueError, OSError) as e:
        return e

def verfi_modprobe():
    try:
        if shutil.which("modprobe"):
            return "modprobe présent"
        else:
            return "modprobe absent"
    except (TypeError, ValueError, OSError) as e:
        return e

    