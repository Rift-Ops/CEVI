# -*- coding: utf-8 -*-
"""
Dossier des actions de CEVI.

Pour ajouter une nouvelle option :

    1. créez un fichier .py dans CE dossier (ex : ma_feature.py) ;
    2. déclarez vos fonctions avec le décorateur @enregistrer_action(...) ;
    3. c'est tout — ce fichier détecte automatiquement tous les modules
       présents ici (ceux commençant par "_" sont ignorés).

Exemple complet dans noyau/registre.py (docstring) et dans les fichiers
diagnostic.py, capture.py, enregistrement.py, connexion.py, installation.py.
"""

import importlib
import pkgutil

for _info in pkgutil.iter_modules(__path__):
    if not _info.name.startswith("_"):
        importlib.import_module(f"{__name__}.{_info.name}")
