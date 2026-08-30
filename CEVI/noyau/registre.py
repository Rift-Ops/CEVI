# -*- coding: utf-8 -*-
"""
registre.py — Cœur du système d'extensions de CEVI.

Comment ajouter une nouvelle option (visible à la fois en ligne de commande
ET dans l'interface graphique) :

    1. Créez un fichier .py dans le dossier "actions/" (ex : actions/mon_option.py)
    2. Importez le décorateur et déclarez votre action :

        from noyau.registre import enregistrer_action, Parametre

        @enregistrer_action(
            "mon_option",
            "Mon option",
            "Ce que fait mon option.",
            parametres=[
                Parametre("mon_nombre", label="Un nombre", type="int", defaut=1),
            ],
        )
        def mon_option(mon_nombre=1):
            print("...")          # les print() s'affichent dans le terminal
            return "Résultat final"   # OU dans la console de la fenêtre graphique

    3. C'est tout : le fichier est détecté automatiquement, l'action apparaît
       dans le menu terminal (python main.py) et dans la fenêtre graphique
       (python main.py -mg), avec un formulaire généré tout seul à partir
       des Parametre déclarés.

    Besoin d'une commande sudo dans votre action ? Utilisez noyau/sudo.py :

        from noyau import sudo
        proc = sudo.lancer(["apt", "install", "-y", "mon-paquet"])

    le mot de passe administrateur est demandé proprement (boîte de dialogue
    en mode graphique, saisie cachée dans le terminal) puis effacé de la
    mémoire à la fin de l'action — ne lancez jamais "sudo" directement.

Types de paramètres acceptés : "str", "int", "float", "bool", "choix".
"""

from dataclasses import dataclass

from noyau import sudo


@dataclass
class Parametre:
    """Description d'un paramètre d'une action.

    nom     : nom technique (envoyé à la fonction Python)
    label   : texte affiché à l'utilisateur (sinon, nom est utilisé)
    type    : "str", "int", "float", "bool" ou "choix"
    defaut  : valeur par défaut si l'utilisateur ne saisit rien
    requis  : True si l'utilisateur doit obligatoirement fournir une valeur
    aide    : petit texte d'aide (info-bulle dans la fenêtre, indice en terminal)
    choix   : tuple des valeurs possibles (uniquement pour type="choix")
    mini    : valeur minimale (types "int" et "float", optionnel)
    maxi    : valeur maximale (types "int" et "float", optionnel)
    """
    nom: str
    label: str = ""
    type: str = "str"
    defaut: object = ""
    requis: bool = False
    aide: str = ""
    choix: tuple = ()
    mini: float = None
    maxi: float = None


@dataclass
class Action:
    """Une action enregistrée : identifiable, affichable et exécutable."""
    identifiant: str
    nom: str
    description: str
    fonction: object
    parametres: list


# Registre interne : identifiant -> Action (l'ordre d'ajout est conservé)
_ACTIONS = {}


def enregistrer_action(identifiant, nom, description="", parametres=None):
    """Décorateur : enregistre une fonction comme action exécutable.

    L'action devient disponible en même temps :
      - dans le menu terminal lancé par main.py (sans argument) ;
      - dans la fenêtre graphique lancée par main.py -mg.
    """
    def decorateur(fonction):
        if identifiant in _ACTIONS:
            print(f"[registre] Attention : l'identifiant '{identifiant}' est déjà "
                  "utilisé, l'ancienne action est remplacée.")
        _ACTIONS[identifiant] = Action(
            identifiant=identifiant,
            nom=nom,
            description=description,
            fonction=fonction,
            parametres=list(parametres or []),
        )
        return fonction
    return decorateur


def actions_triees():
    """Retourne la liste des actions dans l'ordre d'enregistrement."""
    return list(_ACTIONS.values())


def obtenir_action(identifiant):
    """Retourne l'action correspondant à un identifiant, avec un message clair sinon."""
    action = _ACTIONS.get(identifiant)
    if action is None:
        raise ValueError(
            f"Action inconnue : '{identifiant}'. "
            "Utilisez 'python main.py -l' pour voir la liste des actions."
        )
    return action


def convertir_valeur(param, valeur):
    """Convertit une valeur saisie (souvent du texte) vers le type du paramètre.

    Lève ValueError avec un message clair si la valeur est invalide.
    """
    try:
        if param.type == "int":
            return int(str(valeur).strip())
        if param.type == "float":
            return float(str(valeur).strip())
        if param.type == "bool":
            if isinstance(valeur, bool):
                return valeur
            v = str(valeur).strip().lower()
            if v in ("oui", "o", "vrai", "true", "1", "y", "yes"):
                return True
            if v in ("non", "n", "faux", "false", "0", "no"):
                return False
            raise ValueError("répondez par oui/non")
        if param.type == "choix":
            v = str(valeur).strip()
            if v in [str(c) for c in param.choix]:
                return v
            raise ValueError("choisir parmi : " + ", ".join(str(c) for c in param.choix))
        return str(valeur)
    except ValueError as e:
        raise ValueError(
            f"Valeur invalide pour '{param.nom}' (type attendu : {param.type}) "
            f": '{valeur}' ({e})"
        )


def preparer_parametres(action, parametres):
    """Valide les paramètres reçus et prépare les arguments de la fonction.

    - rejette les noms de paramètres inconnus ;
    - convertit chaque valeur vers le type déclaré ;
    - applique les valeurs par défaut ;
    - exige les paramètres marqués requis.
    """
    connus = {p.nom: p for p in action.parametres}
    for cle in parametres:
        if cle not in connus:
            valides = ", ".join(connus) if connus else "(aucun)"
            raise ValueError(
                f"Paramètre inconnu '{cle}' pour '{action.identifiant}'. "
                f"Paramètres acceptés : {valides}"
            )

    kwargs = {}
    for p in action.parametres:
        valeur = parametres.get(p.nom)
        if valeur is None or valeur == "":
            if p.requis:
                raise ValueError(
                    f"Paramètre requis manquant pour '{action.identifiant}' : "
                    f"{p.label or p.nom} ({p.nom})"
                )
            kwargs[p.nom] = p.defaut
        else:
            kwargs[p.nom] = convertir_valeur(p, valeur)
    return kwargs


def executer_action(identifiant, **parametres):
    """Valide les paramètres puis exécute l'action ; retourne son résultat.

    Le mot de passe sudo éventuellement demandé par l'action est effacé
    de la mémoire dès la fin (succès, erreur ou annulation).
    """
    action = obtenir_action(identifiant)
    kwargs = preparer_parametres(action, parametres)
    try:
        return action.fonction(**kwargs)
    finally:
        sudo.oublier()


def resumer_actions():
    """Retourne un texte lisible listant les actions et leurs paramètres."""
    if not _ACTIONS:
        return "Aucune action enregistrée."
    largeur = max(len(a.identifiant) for a in _ACTIONS.values())
    lignes = [f"{len(_ACTIONS)} actions disponibles :", ""]
    for i, a in enumerate(_ACTIONS.values(), 1):
        lignes.append(f"  {i:>2}. {a.identifiant.ljust(largeur)}  {a.nom}")
        if a.description:
            lignes.append(f"      {a.description}")
        for p in a.parametres:
            si_requis = "requis" if p.requis else f"défaut : {p.defaut!r}"
            ligne = f"      - {p.nom} ({p.type}, {si_requis})"
            if p.aide:
                ligne += f" — {p.aide}"
            lignes.append(ligne)
        lignes.append("")
    return "\n".join(lignes).rstrip()
