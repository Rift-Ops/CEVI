# -*- coding: utf-8 -*-
"""
Actions de connexion au téléphone (adb).
Reprend les options 3 et 4 du menu de CEVI.py + une action de déconnexion utile.
Exemples d'actions avec paramètres REQUIS (ip, port).
"""

import os
import subprocess as sps
import time as t

from noyau.registre import enregistrer_action, Parametre
from noyau.chargeur_cevi import charger_cevi
import vrbls


@enregistrer_action(
    "connecter_telephone",
    "Connecter le téléphone (adb)",
    "Reprend le déroulé de l'option 3 de CEVI.py : vérifie si un appareil est "
    "déjà connecté, sinon relance le serveur adb et tente une connexion sans "
    "fil avec l'IP et le port du téléphone sur le réseau local.",
    parametres=[
        Parametre(
            "ip",
            label="IP du téléphone (réseau local)",
            type="str", requis=True,
            aide="Exemple : 192.168.1.24",
        ),
        Parametre(
            "port",
            label="Port",
            type="str", requis=True,
            aide="Exemple : 5555",
        ),
    ],
)
def connecter_telephone(ip="", port=""):
    cevi = charger_cevi()
    try:
        info = sps.run(
            vrbls.adb + ["devices"],
            capture_output=True, text=True, env=os.environ, timeout=15,
        )
        if cevi.appareil_connecte(info.stdout):
            return "Appareil déjà connecté."

        sps.run(vrbls.adb + ["kill-server"])
        print("Connexion en cours...")
        t.sleep(2)
        res = sps.run(
            vrbls.adb + ["connect", f"{ip}:{port}"],
            capture_output=True, env=os.environ, text=True, timeout=30,
        )
        return cevi.analyser_connexion(res.stdout + res.stderr)[1]
    except sps.TimeoutExpired:
        return "Erreur pendant la connexion : adb ne répond pas (délai dépassé)."
    except (OSError, ValueError, TypeError) as e:
        return f"Erreur pendant la connexion : {e}"


@enregistrer_action(
    "appairer_telephone",
    "Appairer le téléphone (adb pair)",
    "Reprend l'option 4 de CEVI.py (jamais implémentée à l'origine) : associe "
    "l'ordinateur au téléphone avec le code à 6 chiffres affiché dans "
    "Options pour les développeurs > Débogage sans fil > Associer l'appareil.",
    parametres=[
        Parametre("ip", label="IP du téléphone (réseau local)", type="str",
                  requis=True, aide="Exemple : 192.168.1.24"),
        Parametre("port", label="Port d'appairage", type="str", requis=True,
                  aide="Port affiché dans la fenêtre d'association (différent de celui de connexion)"),
        Parametre("code", label="Code d'appairage", type="str", requis=True,
                  aide="Code à 6 chiffres affiché sur le téléphone"),
    ],
)
def appairer_telephone(ip="", port="", code=""):
    cevi = charger_cevi()
    try:
        return cevi.appairer_telephone(ip, port, code)[1]
    except sps.TimeoutExpired:
        return "Erreur pendant l'appairage : adb ne répond pas (délai dépassé)."
    except (OSError, ValueError, TypeError) as e:
        return f"Erreur pendant l'appairage : {e}"


@enregistrer_action(
    "deconnecter_adb",
    "Déconnecter le téléphone (adb kill-server)",
    "Arrête le serveur adb de l'ordinateur (coupe aussi les sessions scrcpy adb).",
)
def deconnecter_adb():
    try:
        sps.run(vrbls.adb + ["kill-server"])
        return "Serveur adb arrêté."
    except (OSError, ValueError, TypeError) as e:
        return f"Erreur : {e}"
