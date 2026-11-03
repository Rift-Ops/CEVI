#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py — Point d'entrée unique de CEVI.

Utilisation :
    python main.py                  -> menu interactif en ligne de commande
    python main.py -mg              -> interface graphique (PyQt6)
    python main.py -L en            -> choisit la langue (fr ou en, mémorisée)
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

from noyau import i18n      # noqa: E402
from noyau import registre  # noqa: E402
from noyau.i18n import _    # noqa: E402
import actions              # noqa: E402,F401 — enregistre toutes les actions


def demander_parametres(action):
    """Demande les paramètres d'une action dans le terminal (mode interactif)."""
    valeurs = {}
    for p in action.parametres:
        invite = _(p.label) if p.label else p.nom
        if p.type == "choix":
            invite += f" ({', '.join(str(c) for c in p.choix)})"
        if p.aide:
            invite += f" [{_(p.aide)}]"
        if p.defaut not in ("", None) or p.type == "bool":
            invite += " " + _("(défaut : {defaut})").format(defaut=p.defaut)
        while True:
            brut = input(f"{invite}: ").strip()
            if brut == "" and not p.requis:
                valeurs[p.nom] = p.defaut
                break
            if brut == "" and p.requis:
                print(_("Ce paramètre est obligatoire."))
                continue
            try:
                valeurs[p.nom] = registre.convertir_valeur(p, brut)
                break
            except ValueError as e:
                print(_("Entrée invalide : {e}").format(e=_(str(e))))
    return valeurs


def mode_interactif():
    """Menu numéroté construit automatiquement depuis le registre d'actions."""
    liste = registre.actions_triees()
    while True:
        print("=" * 50)
        print(_("CEVI — menu des options"))
        print("=" * 50)
        print()
        for i, action in enumerate(liste, 1):
            print(f"{i:>2}- {_(action.nom)}")
        print(" L- " + _("Langue") + f" ({i18n.nom_langue(i18n.langue_courante())})")
        print(" 0- " + _("Quitter"))
        choix = input(_("Quel choix prendre: ")).strip()
        if choix == "0":
            print(_("Au revoir !"))
            break
        if choix.lower() == "l":
            i18n.choisir_langue_terminal()
            continue
        if not choix.isdigit() or not (1 <= int(choix) <= len(liste)):
            print(_("Entrée invalide"))
            continue

        action = liste[int(choix) - 1]
        print()
        print(f"--- {_(action.nom)} ---")
        if action.description:
            print(_(action.description))
            print()
        valeurs = demander_parametres(action)
        try:
            resultat = registre.executer_action(action.identifiant, **valeurs)
        except (ValueError, OSError) as e:
            print(_("Erreur : {e}").format(e=_(str(e))))
            continue
        if resultat is None:
            resultat = "Action terminée."
        print()
        print(_("Résultat : {resultat}").format(resultat=i18n.traduire_texte(str(resultat))))


def executer_directe(identifiant, args_bruts):
    """Exécute une action directement depuis la ligne de commande."""
    paires = {}
    for brut in args_bruts:
        if "=" not in brut:
            print(_("Argument invalide : '{brut}' (format attendu : param=valeur)").format(brut=brut))
            sys.exit(1)
        cle, valeur = brut.split("=", 1)
        paires[cle.strip()] = valeur
    try:
        resultat = registre.executer_action(identifiant, **paires)
    except ValueError as e:
        print(_("Erreur : {e}").format(e=_(str(e))))
        print(_("Astuce : 'python main.py -l' montre chaque action et ses paramètres."))
        sys.exit(1)
    if resultat is None:
        resultat = "Action terminée."
    print(_("Résultat : {resultat}").format(resultat=i18n.traduire_texte(str(resultat))))


def mode_graphique():
    """Lance la fenêtre PyQt6, avec des messages clairs si quelque chose manque."""
    try:
        from interface.fenetre import lancer
    except ImportError as e:
        nom = getattr(e, "name", "") or ""
        if "PyQt" in str(e) or "PyQt" in nom:
            print(_("PyQt6 n'est pas installé."))
            print(_("Installez-le avec la commande : pip install PyQt6"))
        else:
            print(_("Impossible de charger l'interface graphique : {e}").format(e=e))
        sys.exit(1)
    try:
        lancer()
    except SystemExit:
        raise
    except BaseException:
        import traceback
        traceback.print_exc()
        print()
        print(_("L'interface graphique n'a pas pu démarrer."))
        print(_("Vérifiez votre installation :  pip install --upgrade PyQt6"))
        sys.exit(1)


def choisir_langue_au_demarrage():
    """Lit --langue/-L avant tout affichage, pour que même l'aide soit traduite."""
    pre = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    pre.add_argument("-L", "--langue")
    connus, _restes = pre.parse_known_args()
    if connus.langue and not i18n.definir_langue(connus.langue, memoriser=True):
        print(_("Langue inconnue : '{code}'. Langues disponibles : {liste}").format(
            code=connus.langue, liste=", ".join(i18n.langues_disponibles())))
        sys.exit(1)
    if not connus.langue:
        i18n.initialiser()


def main():
    choisir_langue_au_demarrage()
    i18n.installer_flux_traduits()
    parseur = argparse.ArgumentParser(
        prog="CEVI",
        description=_("CEVI — lanceur unique : ligne de commande ou interface graphique."),
    )
    parseur.add_argument(
        "-mg", "--mode-graphique", action="store_true",
        help=_("lancer l'interface graphique (PyQt6)"),
    )
    parseur.add_argument(
        "-L", "--langue", metavar="|".join(i18n.langues_disponibles()),
        help=_("langue de l'interface : fr ou en (le choix est mémorisé)"),
    )
    parseur.add_argument(
        "-l", "--liste", action="store_true",
        help=_("afficher la liste des actions disponibles et leurs paramètres"),
    )
    parseur.add_argument(
        "-e", "--executer", metavar="ID",
        help=_("exécuter directement une action (voir les identifiants avec -l)"),
    )
    parseur.add_argument(
        "--args", nargs="*", default=[], metavar="param=valeur",
        help=_("paramètres de l'action, ex : --args ip=192.168.1.24 port=5555"),
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
