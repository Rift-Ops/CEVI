# -*- coding: utf-8 -*-
"""
Actions de diagnostic : vérifier l'environnement sans rien modifier.
Bon exemple d'action sans paramètre.
"""

import glob as g
import os
import subprocess as sps

from noyau.registre import enregistrer_action
from noyau.chargeur_cevi import charger_cevi
import ver_bin as vb
import vrbls


@enregistrer_action(
    "diagnostic",
    "Diagnostic de l'environnement",
    "Vérifie la présence de ffmpeg et modprobe, liste les périphériques /dev/video* "
    "et teste la connexion adb. Aucune modification n'est effectuée sur le système.",
)
def diagnostic():
    cevi = charger_cevi()  # chargé pour montrer l'usage ; non bloquant
    lignes = []

    etat_ffmpeg = str(vb.verfi_ffmpeg())
    print(etat_ffmpeg)
    lignes.append("ffmpeg   : " + etat_ffmpeg)

    etat_modprobe = str(vb.verfi_modprobe())
    print(etat_modprobe)
    lignes.append("modprobe : " + etat_modprobe)

    peripheriques = sorted(g.glob("/dev/video*"))
    if peripheriques:
        print("Périphériques vidéo :", ", ".join(peripheriques))
        lignes.append("Périphériques vidéo : " + ", ".join(peripheriques))
    else:
        print("Périphériques vidéo : aucun (/dev/video*)")
        lignes.append("Périphériques vidéo : aucun (/dev/video*)")

    try:
        info = sps.run(
            vrbls.adb + ["devices"],
            capture_output=True, text=True, env=os.environ, timeout=10,
        )
        detail = info.stdout.strip() or "(réponse vide)"
        print("adb devices :", detail)
        lignes.append("adb devices : " + detail)
    except FileNotFoundError:
        print("adb : introuvable (vérifiez le dossier outils/)")
        lignes.append("adb : introuvable (vérifiez le dossier outils/)")
    except sps.TimeoutExpired:
        print("adb devices : délai dépassé")
        lignes.append("adb devices : délai dépassé")
    except (OSError, ValueError, TypeError) as e:
        print(f"adb : erreur ({e})")
        lignes.append(f"adb : erreur ({e})")

    return "Diagnostic terminé : voir les détails ci-dessus."


@enregistrer_action(
    "lister_peripheriques_video",
    "Lister les périphériques vidéo",
    "Affiche la liste des périphériques /dev/video* présents sur l'ordinateur.",
)
def lister_peripheriques_video():
    peripheriques = sorted(g.glob("/dev/video*"))
    if peripheriques:
        for p in peripheriques:
            print(p)
        return f"{len(peripheriques)} périphérique(s) trouvé(s)."
    print("Aucun périphérique /dev/video* détecté")
    return "Aucun périphérique détecté."


@enregistrer_action(
    "verifier_appli",
    "Vérifier l'application affichée sur le téléphone",
    "Indique si l'application affichée à l'écran du téléphone est supportée "
    "(WhatsApp ou Facebook). Réutilise verifi_quel_appli() de CEVI.py.",
)
def verifier_appli():
    cevi = charger_cevi()
    resultat = cevi.verifi_quel_appli()
    print(resultat)
    return resultat
