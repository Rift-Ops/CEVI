# -*- coding: utf-8 -*-
"""
Actions de capture et d'enregistrement de l'écran du téléphone.
Elles reprennent le déroulé des options 1 et 2 du menu de CEVI.py,
en réutilisant ses fonctions via le chargeur (sans le modifier).
Exemples d'actions AVEC paramètres (formulaire généré automatiquement en GUI).
"""

import datetime as dt
import os
import subprocess as sps
import time as t

from noyau.registre import enregistrer_action, Parametre
from noyau.chargeur_cevi import charger_cevi
from noyau import sudo
import ver_bin as vb
import vrbls


@enregistrer_action(
    "capture_ecran",
    "Capture d'écran du téléphone",
    "Reprend le déroulé de l'option 1 de CEVI.py : vérifie ffmpeg et modprobe, "
    "vérifie/active v4l2loopback, lance scrcpy vers le périphérique vidéo choisi "
    "puis capture une image avec ffmpeg.",
    parametres=[
        Parametre(
            "numero_video",
            label="Numéro du périphérique vidéo",
            type="int", defaut=2, mini=0,
            aide="scrcpy envoie le flux vers /dev/video<N> ; la capture finale "
                 "lit /dev/video2 (voir capture_directe dans CEVI.py)",
        ),
    ],
)
def capture_ecran(numero_video=2):
    cevi = charger_cevi()
    try:
        etat_ffmpeg = str(vb.verfi_ffmpeg())
        print(etat_ffmpeg)
        if "absent" in etat_ffmpeg:
            return "ffmpeg absent : utilisez l'action 'installer_ffmpeg' puis relancez."

        etat_modprobe = str(vb.verfi_modprobe())
        print(etat_modprobe)
        if "absent" in etat_modprobe:
            return "modprobe absent : utilisez l'action 'installer_modprobe' puis relancez."

        # Chargement du module v4l2loopback via noyau/sudo.py : le mot de
        # passe est demandé explicitement (dialogue en graphique, saisie
        # cachée en terminal). C'est l'équivalent fiable de la séquence
        # verifi_v4l2loopback() + lancement_v4l2loopback() de CEVI.py, qui
        # ne peut pas fonctionner en mode graphique car elle lance sudo
        # sans pouvoir fournir de mot de passe.
        print("Chargement du module v4l2loopback (mot de passe demandé si nécessaire)...")
        try:
            proc_charge = sudo.lancer(["modprobe", "v4l2loopback"],
                                      afficher_sortie=False)
        except sudo.ErreurSudo as e:
            return str(e)
        if proc_charge.returncode != 0:
            return ("Impossible de charger v4l2loopback :\n"
                    + sudo.dernieres_lignes(proc_charge.stderr, 3)
                    + "\nSi le module n'est pas installé, lancez d'abord les "
                      "actions 'installer_headers' et 'installer_v4l2loopback'.")
        print("module v4l2loopback chargé")
        cevi.list_ecran_v()

        print(f"Lancement de scrcpy vers /dev/video{numero_video}...")
        cevi.scrcpy_arrpl(str(numero_video))
        print("Attente de 2 secondes pour le démarrage du flux...")
        t.sleep(2)

        etat_appli = cevi.verifi_quel_appli()
        print(etat_appli)
        if "supportée" in etat_appli:
            cevi.capture_directe()
            return "Capture d'écran effectuée."
        else:
            print("Appli non supportée, arrêt du serveur adb...")
            try:
                sps.run(vrbls.adb + ["kill-server"])
            except (OSError, ValueError, TypeError) as e:
                print(e)
            return "Appli non supportée : ouvrez WhatsApp ou Facebook sur le " \
                   "téléphone puis relancez."
    except (OSError, ValueError, TypeError) as e:
        return f"Erreur pendant la capture : {e}"


@enregistrer_action(
    "enregistrer_ecran",
    "Enregistrement d'écran du téléphone",
    "Reprend le déroulé de l'option 2 de CEVI.py : vérifie l'application affichée, "
    "enregistre l'écran du téléphone via scrcpy pendant la durée choisie, puis "
    "décharge le module v4l2loopback.",
    parametres=[
        Parametre(
            "duree",
            label="Durée (secondes)",
            type="int", defaut=10, mini=1,
            aide="Durée de l'enregistrement en secondes",
        ),
        Parametre(
            "nom_fichier",
            label="Nom du fichier",
            type="str", defaut="",
            aide="Laissez vide pour un nom automatique basé sur la date et l'heure",
        ),
    ],
)
def enregistrer_ecran(duree=10, nom_fichier=""):
    cevi = charger_cevi()
    try:
        etat_appli = cevi.verifi_quel_appli()
        print(etat_appli)
        if "non" in etat_appli:
            return "Appli non supportée : ouvrez WhatsApp ou Facebook sur le " \
                   "téléphone puis relancez."

        if not nom_fichier:
            nom_fichier = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_enregistrement.mp4"

        vraie_seconde = (duree * 10) / 9  # calibrage identique à CEVI.py
        print(f"Enregistrement lancé pour {duree} secondes...")
        cmd = vrbls.scrcpy + ["-r", nom_fichier, "--no-window"]
        proc = sps.Popen(cmd, env=os.environ)
        t.sleep(vraie_seconde)
        proc.terminate()
        proc.wait()
        print("Enregistrement terminé avec succès")

        print("Désactivation du module v4l2loopback...")
        try:
            proc_retire = sudo.lancer(["modprobe", "-r", "v4l2loopback"],
                                      afficher_sortie=False)
            if proc_retire.returncode != 0:
                print("Impossible de décharger v4l2loopback : "
                      + sudo.dernieres_lignes(proc_retire.stderr, 2))
        except sudo.ErreurSudo as e:
            # étape de nettoyage : non bloquante si le mot de passe est refusé
            print(f"Désactivation ignorée : {e}")
        except (OSError, ValueError, TypeError) as e:
            print(e)

        return f"Enregistrement terminé : {nom_fichier}"
    except (OSError, ValueError, TypeError) as e:
        return f"Erreur pendant l'enregistrement : {e}"
