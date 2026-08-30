# -*- coding: utf-8 -*-
"""
chargeur_cevi.py — Chargement de CEVI.py en tant que bibliothèque.

CEVI.py appelle start() à sa dernière ligne : un import classique exécuterait
donc le menu interactif dès le chargement. Pour réutiliser les fonctions de
CEVI.py (capture, enregistrement, connexion...) SANS TOUCHER AU FICHIER,
ce chargeur :

    1. lit CEVI.py sur le disque (le fichier reste strictement inchangé) ;
    2. neutralise UNIQUEMENT l'appel final "start()" dans le code chargé
       en mémoire (jamais sur le disque) ;
    3. bloque input() pendant le chargement, au cas où la neutralisation
       échouerait après une modification de CEVI.py (erreur claire au lieu
       d'un menu bloquant) ;
    4. exécute ce code dans un module Python mis en cache.

Toutes les fonctions de CEVI.py restent ensuite utilisables normalement :
    cevi = charger_cevi()
    cevi.capture_directe()
"""

import builtins
import os
import sys
import types

_module = None


def charger_cevi():
    """Retourne le module CEVI, chargé une seule fois et sans exécuter start()."""
    global _module
    if _module is not None:
        return _module

    racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if racine not in sys.path:
        sys.path.insert(0, racine)

    chemin = os.path.join(racine, "CEVI.py")
    try:
        with open(chemin, "r", encoding="utf-8") as fichier:
            source = fichier.read()
    except OSError as e:
        raise RuntimeError(f"Impossible de lire CEVI.py ({chemin}) : {e}")

    code = source.rstrip()
    if code.endswith("start()"):
        code = code[: -len("start()")] + (
            "pass  # start() neutralisé EN MÉMOIRE : CEVI est chargé comme bibliothèque"
        )

    module = types.ModuleType("CEVI")
    module.__file__ = chemin
    sys.modules["CEVI"] = module

    entree_originale = builtins.input

    def _input_bloque(*args, **kwargs):
        raise RuntimeError(
            "input() a été appelé pendant le chargement de CEVI.py : "
            "la neutralisation de start() a échoué, le fichier a peut-être "
            "été modifié."
        )

    builtins.input = _input_bloque
    try:
        exec(compile(code, chemin, "exec"), module.__dict__)
    finally:
        builtins.input = entree_originale

    _module = module
    return module
