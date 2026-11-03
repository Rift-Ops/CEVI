# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Pul-07 — CEVI est un logiciel libre sous licence GNU GPL v3 (voir LICENSE).
"""
i18n.py — Langues de CEVI (français / anglais).

Principe : le code source de CEVI est écrit en français. Le français est donc
la langue « de référence » : un texte français sert de clé, et le catalogue
de chaque autre langue (noyau/traductions.py) donne sa traduction.
Un texte absent du catalogue s'affiche simplement en français : une
traduction manquante ne casse jamais le programme.

    from noyau.i18n import _
    print(_("Au revoir !"))                       # -> "Goodbye!" en anglais
    _("Erreur : {e}").format(e=erreur)            # texte à trous

Les textes à trous ("{nom}") sont aussi reconnus APRÈS mise en forme, ce qui
permet de traduire un message déjà construit par une f-string :
    _("Enregistrement terminé : 2026.mp4")        # -> "Recording finished: 2026.mp4"

Choix de la langue (par ordre de priorité) :
    1. option de ligne de commande  --langue fr|en  (ou -L)
    2. variable d'environnement      CEVI_LANG
    3. langue mémorisée              ~/.config/cevi/langue
    4. langue du système (LANG)      si elle est disponible
    5. français

Ajouter une langue : créez un dictionnaire dans traductions.py, ajoutez-le à
CATALOGUES et à NOMS_LANGUES. Elle apparaît seule dans les menus.
"""

import locale
import os
import re
import sys

from noyau import traductions

LANGUE_REFERENCE = "fr"
NOMS_LANGUES = {"fr": "Français", "en": "English"}
CATALOGUES = {"en": traductions.EN}

_langue = LANGUE_REFERENCE
_modeles = {}   # langue -> liste de (regex, traduction) pour les textes à trous


def langues_disponibles():
    """Codes des langues proposées, la langue de référence en premier."""
    return [LANGUE_REFERENCE] + [c for c in NOMS_LANGUES if c != LANGUE_REFERENCE
                                  and c in CATALOGUES]


def nom_langue(code):
    return NOMS_LANGUES.get(code, code)


def langue_courante():
    return _langue


def _normaliser(code):
    """'en_US.UTF-8' -> 'en' ; retourne None si la langue est inconnue."""
    if not code:
        return None
    court = str(code).strip().lower().replace("-", "_").split("_")[0].split(".")[0]
    return court if court in langues_disponibles() else None


def definir_langue(code, memoriser=False):
    """Change la langue active. Retourne True si le code est valide."""
    global _langue
    court = _normaliser(code)
    if court is None:
        return False
    _langue = court
    if memoriser:
        _sauver_langue(court)
    return True


# ------------------------------------------------------------ mémorisation

def _fichier_config():
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "cevi", "langue")


def _sauver_langue(code):
    try:
        chemin = _fichier_config()
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(code + "\n")
    except OSError:
        pass  # la mémorisation est facultative


def _lire_langue_memorisee():
    try:
        with open(_fichier_config(), "r", encoding="utf-8") as f:
            return _normaliser(f.read())
    except OSError:
        return None


def initialiser(code_demande=None):
    """Détermine la langue au démarrage (voir l'ordre de priorité en tête de fichier)."""
    candidats = [code_demande, os.environ.get("CEVI_LANG"), _lire_langue_memorisee()]
    try:
        candidats.append(locale.getlocale()[0])
    except (ValueError, TypeError):
        pass
    candidats.append(os.environ.get("LANG"))
    for c in candidats:
        if _normaliser(c):
            definir_langue(c)
            return _langue
    definir_langue(LANGUE_REFERENCE)
    return _langue


# -------------------------------------------------------------- traduction

def _modeles_de(langue):
    """Compile (une fois) les textes à trous du catalogue en expressions régulières."""
    if langue not in _modeles:
        liste = []
        for source, cible in CATALOGUES.get(langue, {}).items():
            if "{" not in source:
                continue
            motif = re.escape(source)
            motif = re.sub(r"\\\{(\w+)\\\}", r"(?P<\1>.*?)", motif)
            liste.append((re.compile("^" + motif + r"\Z", re.S), cible))
        # les modèles les plus longs (les plus précis) passent en premier
        liste.sort(key=lambda m: -len(m[0].pattern))
        _modeles[langue] = liste
    return _modeles[langue]


def _(texte):
    """Traduit un texte français dans la langue active (sinon le rend tel quel)."""
    if _langue == LANGUE_REFERENCE or not isinstance(texte, str) or not texte.strip():
        return texte
    catalogue = CATALOGUES.get(_langue, {})
    if texte in catalogue:
        return catalogue[texte]
    for motif, cible in _modeles_de(_langue):
        m = motif.match(texte)
        if m:
            try:
                # les morceaux variables sont eux aussi traduits (ex. un message
                # d'erreur français inséré dans « Erreur : {e} »)
                return cible.format(**{k: _morceau(v) for k, v in m.groupdict().items()})
            except (KeyError, IndexError, ValueError):
                return texte
    return texte


def _morceau(texte):
    """Traduit un morceau variable en conservant les espaces qui l'entourent."""
    coeur = texte.strip()
    if not coeur:
        return texte
    debut = texte[:len(texte) - len(texte.lstrip())]
    fin = texte[len(texte.rstrip()):]
    return debut + _(coeur) + fin


def traduire_texte(texte):
    """Traduit un texte de plusieurs lignes : d'abord en bloc (messages composés
    de plusieurs lignes), sinon ligne par ligne. Les sauts de ligne finaux sont
    toujours conservés."""
    if _langue == LANGUE_REFERENCE or not texte:
        return texte
    corps = texte.rstrip("\r\n")
    fin = texte[len(corps):]
    entier = _(corps)
    if entier != corps:
        return entier + fin
    return "".join(_ligne(l) for l in texte.splitlines(keepends=True))


def _ligne(ligne):
    fin = ligne[len(ligne.rstrip("\r\n")):]
    return _(ligne[:len(ligne) - len(fin)]) + fin


class TamponLignes:
    """Reçoit le texte par morceaux (print écrit « texte », « \\n » séparément)
    et rend les lignes COMPLÈTES, déjà traduites."""

    def __init__(self):
        self._reste = ""

    def ecrire(self, texte):
        self._reste += texte
        if "\n" not in self._reste:
            return ""
        complet, _sep, self._reste = self._reste.rpartition("\n")
        return traduire_texte(complet + "\n")

    def vider(self):
        reste, self._reste = self._reste, ""
        return traduire_texte(reste)


class FluxTraduit:
    """Enveloppe de sys.stdout / sys.stderr qui traduit chaque ligne affichée."""

    def __init__(self, flux):
        self._flux = flux
        self._tampon = TamponLignes()

    def write(self, texte):
        sortie = self._tampon.ecrire(str(texte))
        if sortie:
            self._flux.write(sortie)
        return len(texte)

    def flush(self):
        reste = self._tampon.vider()
        if reste:
            self._flux.write(reste)
        self._flux.flush()

    def isatty(self):
        return getattr(self._flux, "isatty", lambda: False)()

    def __getattr__(self, nom):
        return getattr(self._flux, nom)


def installer_flux_traduits():
    """Traduit tout ce qui est affiché par print() dans le terminal."""
    if not isinstance(sys.stdout, FluxTraduit):
        sys.stdout = FluxTraduit(sys.stdout)
    if not isinstance(sys.stderr, FluxTraduit):
        sys.stderr = FluxTraduit(sys.stderr)


def choisir_langue_terminal():
    """Petit menu du terminal pour changer de langue (choix mémorisé)."""
    codes = langues_disponibles()
    print(_("Langue :"))
    for i, code in enumerate(codes, 1):
        marque = " *" if code == _langue else ""
        print(f" {i}- {nom_langue(code)}{marque}")
    choix = input(_("Numéro de la langue (Entrée pour annuler) : ")).strip()
    if choix.isdigit() and 1 <= int(choix) <= len(codes):
        definir_langue(codes[int(choix) - 1], memoriser=True)
        print(_("Langue changée : {langue}").format(langue=nom_langue(_langue)))
    elif choix:
        print(_("Entrée invalide"))
