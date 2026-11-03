# -*- coding: utf-8 -*-
"""Chemins des outils externes (adb, scrcpy).

Ordre de recherche pour chaque outil :
  1. le dossier "outils/" situé à côté de ce fichier (extrait de outils.zip) ;
  2. l'outil installé sur le système (présent dans le PATH).

Les chemins sont absolus : ils fonctionnent quel que soit le dossier depuis
lequel CEVI est lancé (avant, "outils/adb" ne marchait que si le dossier
courant était celui du projet).
"""

import os
import shutil

_DOSSIER = os.path.dirname(os.path.abspath(__file__))


def _chemin_outil(nom):
    local = os.path.join(_DOSSIER, "outils", nom)
    if os.path.isfile(local) and os.access(local, os.X_OK):
        return [local]
    systeme = shutil.which(nom)
    if systeme:
        return [systeme]
    # Introuvable : on garde le chemin local pour obtenir une erreur claire
    # (FileNotFoundError) que les actions savent afficher.
    return [local]


scrcpy = _chemin_outil("scrcpy")
adb = _chemin_outil("adb")
