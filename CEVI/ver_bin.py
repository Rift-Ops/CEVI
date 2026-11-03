# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Pul-07 — CEVI est un logiciel libre sous licence GNU GPL v3 (voir LICENSE).
import os
import shutil

# modprobe/modinfo se trouvent dans /sbin ou /usr/sbin, des dossiers absents du
# PATH d'un utilisateur normal sous Debian : sans cela ils étaient déclarés
# "absents" alors qu'ils sont installés.
_CHEMIN_ETENDU = os.environ.get("PATH", "") + os.pathsep + "/sbin" + os.pathsep + "/usr/sbin"


def trouver_binaire(nom):
    """Retourne le chemin complet d'un programme (PATH + sbin) ou None."""
    return shutil.which(nom, path=_CHEMIN_ETENDU)


def verfi_ffmpeg():
    try:
        if trouver_binaire("ffmpeg"):
            return "ffmpeg présent"
        else:
            return "ffmpeg absent"
    except (TypeError, ValueError, OSError) as e:
        return str(e)


def verfi_modprobe():
    try:
        if trouver_binaire("modprobe"):
            return "modprobe présent"
        else:
            return "modprobe absent"
    except (TypeError, ValueError, OSError) as e:
        return str(e)
