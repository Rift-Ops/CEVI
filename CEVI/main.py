#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py — Point d'entrée unique de CEVI.

Utilisation :
    python main.py                  -> menu interactif en ligne de commande
    python main.py -mg              -> interface graphique (PyQt6)
    python main.py -l               -> liste des actions disponibles
    python main.py -e diagnostic    -> exécute directement une action
    python main.py -e connecter_telephone --args ip=192.168.1.24 port=5555

Les fichiers d'origine (CEVI.py, vrbls.py, ver_bin.py) ne sont pas modifiés :
    python CEVI.py                  -> fonctionne toujours comme avant.

Pour ajouter une nouvelle option, voir la docstring de noyau/registre.py :
il suffit de créer un fichier dans actions/ avec le décorateur
@enregistrer_action — l'option devient disponible en terminal ET en fenêtre
graphique automatiquement.
"""

import argparse
import os
import sys

# Le dossier du projet est ajouté au chemin Python et devient le dossier
# courant : cela garantit que "outils/adb" et "outils/scrcpy" (définis dans
# vrbls.py avec des chemins relatifs) sont trouvés, peu importe d'où la
# commande est lancée.
RACINE = os.path.dirname(os.path.abspath(__file__))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)
os.chdir(RACINE)

from noyau import registre  # noqa: E402
import actions              # noqa: E402,F401 — enregistre toutes les actions


def demander_parametres(action):
    """Demande les paramètres d'une action dans le terminal (mode interactif)."""
    valeurs = {}
    for p in action.parametres:
        invite = p.label or p.nom
        if p.type == "choix":
            invite += f" ({', '.join(str(c) for c in p.choix)})"
        if p.aide:
            invite += f" [{p.aide}]"
        if p.defaut not in ("", None) or p.type == "bool":
            invite += f" (défaut : {p.defaut})"
        while True:
            brut = input(f"{invite}: ").strip()
            if brut == "" and not p.requis:
                valeurs[p.nom] = p.defaut
                break
            if brut == "" and p.requis:
                print("Ce paramètre est obligatoire.")
                continue
            try:
                valeurs[p.nom] = registre.convertir_valeur(p, brut)
                break
            except ValueError as e:
                print(f"Entrée invalide : {e}")
    return valeurs


def mode_interactif():
    """Menu numéroté construit automatiquement depuis le registre d'actions."""
    liste = registre.actions_triees()
    print("=" * 50)
    print("CEVI — menu des options")
    print("=" * 50)
    while True:
        print()
        for i, action in enumerate(liste, 1):
            print(f"{i:>2}- {action.nom}")
        print(" 0- Quitter")
        choix = input("Quelle choix prendre: ").strip()
        if choix == "0":
            print("Au revoir !")
            break
        if not choix.isdigit() or not (1 <= int(choix) <= len(liste)):
            print("Entrée invalide")
            continue

        action = liste[int(choix) - 1]
        print()
        print(f"--- {action.nom} ---")
        if action.description:
            print(action.description)
            print()
        valeurs = demander_parametres(action)
        try:
            resultat = registre.executer_action(action.identifiant, **valeurs)
        except (ValueError, OSError) as e:
            print(f"Erreur : {e}")
            continue
        if resultat is None:
            resultat = "Action terminée."
        print()
        print(f"Résultat : {resultat}")


def executer_directe(identifiant, args_bruts):
    """Exécute une action directement depuis la ligne de commande."""
    paires = {}
    for brut in args_bruts:
        if "=" not in brut:
            print(f"Argument invalide : '{brut}' (format attendu : param=valeur)")
            sys.exit(1)
        cle, valeur = brut.split("=", 1)
        paires[cle.strip()] = valeur
    try:
        resultat = registre.executer_action(identifiant, **paires)
    except ValueError as e:
        print(f"Erreur : {e}")
        print("Astuce : 'python main.py -l' montre chaque action et ses paramètres.")
        sys.exit(1)
    if resultat is None:
        resultat = "Action terminée."
    print(f"Résultat : {resultat}")


def mode_graphique():
    """Lance la fenêtre PyQt6, avec des messages clairs si quelque chose manque."""
    try:
        from interface.fenetre import lancer
    except ImportError as e:
        nom = getattr(e, "name", "") or ""
        if "PyQt" in str(e) or "PyQt" in nom:
            print("PyQt6 n'est pas installé.")
            print("Installez-le avec la commande : pip install PyQt6")
        else:
            print(f"Impossible de charger l'interface graphique : {e}")
        sys.exit(1)
    try:
        lancer()
    except SystemExit:
        raise
    except BaseException:
        import traceback
        traceback.print_exc()
        print()
        print("L'interface graphique n'a pas pu démarrer.")
        print("Vérifiez votre installation :  pip install --upgrade PyQt6")
        sys.exit(1)


def main():
    parseur = argparse.ArgumentParser(
        prog="CEVI",
        description="CEVI — lanceur unique : ligne de commande ou interface graphique.",
    )
    parseur.add_argument(
        "-mg", "--mode-graphique", action="store_true",
        help="lancer l'interface graphique (PyQt6)",
    )
    parseur.add_argument(
        "-l", "--liste", action="store_true",
        help="afficher la liste des actions disponibles et leurs paramètres",
    )
    parseur.add_argument(
        "-e", "--executer", metavar="ID",
        help="exécuter directement une action (voir les identifiants avec -l)",
    )
    parseur.add_argument(
        "--args", nargs="*", default=[], metavar="param=valeur",
        help="paramètres de l'action, ex : --args ip=192.168.1.24 port=5555",
    )
    args = parseur.parse_args()

    if args.mode_graphique:
        mode_graphique()
    elif args.executer:
        executer_directe(args.executer, args.args)
    elif args.liste:
        print(registre.resumer_actions())
    else:
        mode_interactif()


if __name__ == "__main__":
    main()
