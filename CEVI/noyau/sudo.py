# -*- coding: utf-8 -*-
"""
sudo.py — commandes administrateur avec demande EXPLICITE du mot de passe.

Pourquoi ce module ?
    Les fonctions d'origine de CEVI.py lancent des commandes « sudo » sans
    pouvoir fournir de mot de passe : en mode graphique il n'y a aucun
    terminal, sudo échoue donc avec une erreur. Ce module résout le problème
    en demandant le mot de passe au moment précis où il est nécessaire :
      - mode graphique : une boîte de dialogue s'ouvre (champ masqué) ;
      - terminal : saisie cachée (getpass), rien ne s'affiche à l'écran.

Sécurité :
    - le mot de passe n'est jamais affiché, ni écrit sur le disque, ni
      transmis à la console ;
    - il reste en mémoire uniquement le temps de l'action en cours, pour
      éviter de le redemander à chaque commande sudo de la même action ;
    - il est effacé automatiquement dès la fin de l'action (oublier()).

Comment l'utiliser dans une NOUVELLE action (dossier actions/) :

    from noyau import sudo

    @enregistrer_action("mon_install", "Mon installation", "...")
    def mon_install():
        proc = sudo.lancer(["apt", "install", "-y", "mon-paquet"])
        if proc.returncode == 0:
            return "Installé."
        return "Échec : " + sudo.dernieres_lignes(proc.stderr, 3)

    Remarques :
      - passez la commande SANS "sudo" (il est ajouté automatiquement) ;
      - sudo.ErreurSudo est levée si l'utilisateur annule la demande ou se
        trompe 3 fois : attrapez-la pour renvoyer un message propre ;
      - ne lancez jamais subprocess avec "sudo" directement : cela
        reproduirait le bug « aucune erreur visible / impossible de
        saisir le mot de passe » en mode graphique.
"""

import getpass
import shutil
import subprocess as sps
import sys

# État interne du module ---------------------------------------------------
_mot_de_passe = None   # en mémoire pour l'action en cours uniquement
_demandeur = None      # fonction(titre, message) -> mot de passe (GUI)

_TENTATIVES = 3           # essais de mot de passe avant abandon
_DELAI_VALIDATION = 30    # secondes max pour vérifier le mot de passe
_DELAI_DIALOGUE = 600     # secondes max d'attente de la boîte graphique


class ErreurSudo(Exception):
    """Mot de passe annulé, refusé, ou impossible à demander."""


def fixuer_demandeur(fonction):
    """Enregistre la façon de demander le mot de passe (mode graphique).

    La fonction reçoit (titre, message) et retourne le mot de passe saisi,
    ou None si l'utilisateur annule. Elle doit pouvoir être appelée depuis
    un thread d'arrière-plan (voir Fenetre.demander_mot_de_passe, qui est
    sûre pour les threads via un signal Qt).
    """
    global _demandeur
    _demandeur = fonction


def oublier():
    """Efface le mot de passe de la mémoire.

    Appelé automatiquement à la fin de chaque action (CLI comme GUI) :
    le mot de passe ne survit jamais à l'action qui l'a demandé.
    """
    global _mot_de_passe
    _mot_de_passe = None


def dernieres_lignes(texte, n=3):
    """Retourne les n dernières lignes non vides d'un texte de sortie,
    pour afficher un message d'erreur utile sans noyer la console."""
    if not texte or not str(texte).strip():
        return "(aucun message d'erreur)"
    lignes = [l.strip() for l in str(texte).strip().splitlines() if l.strip()]
    return "\n".join(lignes[-n:])


def _demander(titre, message):
    """Demande le mot de passe par le canal disponible et le mémorise."""
    global _mot_de_passe
    if _demandeur is not None:
        # mode graphique : boîte de dialogue (sûr pour les threads)
        mot = _demandeur(titre, message)
    elif sys.stdin is not None and sys.stdin.isatty():
        # terminal : saisie cachée, rien ne s'affiche à l'écran
        print(titre)
        if message:
            print(message)
        mot = getpass.getpass("Mot de passe (sudo) : ")
    else:
        raise ErreurSudo(
            "Un mot de passe administrateur (sudo) est requis, mais aucun "
            "moyen de le demander n'est disponible (ni interface graphique, "
            "ni terminal interactif)."
        )
    if not mot:
        raise ErreurSudo("Mot de passe non fourni : opération annulée.")
    _mot_de_passe = str(mot)
    return _mot_de_passe


def _valider(mot_de_passe):
    """Vérifie le mot de passe auprès de sudo.

    Utilise « sudo -S -k -v » : le code retour (0 = correct) est fiable
    quelle que soit la langue du système, contrairement aux messages texte.
    Retourne True si le mot de passe est accepté, False sinon.
    """
    try:
        proc = sps.run(
            ["sudo", "-S", "-k", "-p", "", "-v"],
            input=mot_de_passe + "\n",
            stdout=sps.PIPE, stderr=sps.PIPE, text=True,
            timeout=_DELAI_VALIDATION,
        )
        return proc.returncode == 0
    except sps.TimeoutExpired:
        return False
    except (OSError, ValueError):
        # sudo introuvable ou environnement anormal : le signaler via lancer()
        return False


def lancer(commande, titre="Mot de passe administrateur requis",
           message="Cette action doit exécuter une commande avec les droits "
                   "administrateur (sudo).",
           tentatives=_TENTATIVES, timeout=None, afficher_sortie=True):
    """Exécute `commande` (liste, SANS « sudo ») avec élévation de droits.

    Déroulement :
      1. demande le mot de passe explicitement (dialogue graphique ou
         saisie cachée dans le terminal), sauf s'il est déjà connu de
         l'action en cours ;
      2. le vérifie auprès de sudo (tentatives essais maximum) ;
      3. lance la commande et retourne un subprocess.CompletedProcess
         (attributs .returncode, .stdout, .stderr).

    Lève ErreurSudo si l'utilisateur annule la demande, si le mot de passe
    est refusé après `tentatives` essais, ou si sudo est indisponible.
    """
    global _mot_de_passe

    if shutil.which("sudo") is None:
        raise ErreurSudo("La commande sudo est introuvable sur ce système.")

    mot = None
    for essai in range(1, max(1, tentatives) + 1):
        mot = _mot_de_passe or _demander(titre, message)
        if _valider(mot):
            _mot_de_passe = mot
            break
        _mot_de_passe = None
        print(f"Mot de passe refusé par sudo (essai {essai}/{tentatives}).")
    else:
        raise ErreurSudo(
            f"Mot de passe incorrect après {tentatives} tentatives : "
            "opération abandonnée."
        )

    cmd = ["sudo", "-S", "-p", "", "--"] + list(commande)
    if afficher_sortie:
        print("Commande lancée : sudo " + " ".join(str(c) for c in commande))
    try:
        proc = sps.run(
            cmd,
            input=mot + "\n",
            stdout=sps.PIPE, stderr=sps.PIPE, text=True,
            timeout=timeout,
        )
    except sps.TimeoutExpired:
        raise ErreurSudo(
            "La commande sudo a dépassé le temps imparti et a été interrompue."
        )
    except (OSError, ValueError) as e:
        raise ErreurSudo(f"Impossible de lancer sudo : {e}")

    if afficher_sortie:
        if proc.stdout and proc.stdout.strip():
            print(proc.stdout.rstrip())
        if proc.stderr and proc.stderr.strip():
            print(proc.stderr.rstrip())
    return proc
