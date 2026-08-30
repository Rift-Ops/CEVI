# -*- coding: utf-8 -*-
"""
Actions d'installation des dépendances (nécessitent les droits sudo).

Le mot de passe administrateur est demandé EXPLICITEMENT au moment
nécessaire, au lieu de laisser sudo échouer en silence :
  - mode graphique : une boîte de dialogue s'ouvre (champ masqué) ;
  - terminal : saisie cachée (aucun caractère affiché).

Le mot de passe n'est jamais affiché ni enregistré : il est gardé en
mémoire le temps de l'action, puis effacé automatiquement.

Ces actions reprennent les MÊMES commandes que les fonctions
d'installation de CEVI.py (fichier d'origine, non modifié), mais passent
par noyau/sudo.py pour que le mot de passe puisse être fourni. Seule
différence volontaire : « -y » est ajouté à l'installation de
v4l2loopback (absent dans CEVI.py) pour éviter qu'apt n'attende une
confirmation qui ne viendrait jamais.
"""

from noyau.registre import enregistrer_action
from noyau import sudo


def _installer(paquets, nom):
    """Lance 'sudo apt install <paquets> -y' avec demande du mot de passe."""
    try:
        proc = sudo.lancer(["apt", "install"] + list(paquets) + ["-y"])
    except sudo.ErreurSudo as e:
        return str(e)
    if proc.returncode == 0:
        return f"Installation de {nom} terminée."
    return (f"Échec de l'installation de {nom} "
            f"(code retour {proc.returncode}) :\n"
            + sudo.dernieres_lignes(proc.stderr, 4))


@enregistrer_action(
    "installer_ffmpeg",
    "Installer ffmpeg",
    "Installe ffmpeg (sudo apt install ffmpeg -y). Le mot de passe "
    "administrateur est demandé explicitement : dialogue en mode graphique, "
    "saisie cachée dans le terminal.",
)
def installer_ffmpeg():
    return _installer(["ffmpeg"], "ffmpeg")


@enregistrer_action(
    "installer_modprobe",
    "Installer modprobe",
    "Installe modprobe (sudo apt install modprobe -y). Le mot de passe "
    "administrateur est demandé explicitement : dialogue en mode graphique, "
    "saisie cachée dans le terminal.",
)
def installer_modprobe():
    return _installer(["modprobe"], "modprobe")


@enregistrer_action(
    "installer_headers",
    "Installer les en-têtes Linux",
    "Installe linux-headers-generic (sudo apt install linux-headers-generic -y), "
    "comme install_linux_headers_generic de CEVI.py. Le mot de passe "
    "administrateur est demandé explicitement.",
)
def installer_headers():
    return _installer(["linux-headers-generic"], "linux-headers-generic")


@enregistrer_action(
    "installer_v4l2loopback",
    "Installer v4l2loopback",
    "Installe v4l2loopback-dkms et v4l2loopback-utils (sudo apt install ... -y), "
    "comme install_v4l2loopback de CEVI.py. Le mot de passe administrateur est "
    "demandé explicitement.",
)
def installer_v4l2loopback():
    return _installer(["v4l2loopback-dkms", "v4l2loopback-utils"], "v4l2loopback")


@enregistrer_action(
    "lancer_v4l2loopback",
    "Charger le module v4l2loopback",
    "Lance 'sudo modprobe v4l2loopback' pour activer la caméra virtuelle. "
    "Le mot de passe administrateur est demandé explicitement (dialogue en "
    "mode graphique, saisie cachée dans le terminal).",
)
def lancer_v4l2loopback():
    try:
        proc = sudo.lancer(["modprobe", "v4l2loopback"])
    except sudo.ErreurSudo as e:
        return str(e)
    if proc.returncode == 0:
        return "Module v4l2loopback chargé."
    return (f"Échec du chargement de v4l2loopback "
            f"(code retour {proc.returncode}) :\n"
            + sudo.dernieres_lignes(proc.stderr, 4)
            + "\nSi le module n'est pas installé, lancez d'abord les actions "
              "'installer_headers' et 'installer_v4l2loopback'.")
