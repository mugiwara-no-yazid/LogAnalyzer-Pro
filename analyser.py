from pathlib import Path
import os
import platform
   
def tri_dict(dictionnaire):
    """
    Trie un dictionnaire par valeurs dans l'ordre décroissant.

    Convertit les paires clé-valeur en liste de listes, puis applique
    un algorithme de tri à bulles pour les ordonner de la plus grande
    à la plus petite valeur.

    :param dictionnaire: Dictionnaire dont les valeurs sont comparables (int, float, etc.)
    :type dictionnaire: dict
    :return: Liste de paires [clé, valeur] triées par valeur décroissante
    :rtype: list[list]

    :exemple:
        >>> tri_dict({"a": 1, "b": 3, "c": 2})
        [['b', 3], ['c', 2], ['a', 1]]
    """
    items = [list(item) for item in dictionnaire.items()]
    n = len(items)
    for i in range(n):
        for j in range(0, n - i - 1):
            if items[j][1] < items[j + 1][1]:
                items[j], items[j + 1] = items[j + 1], items[j]
    return items
    
def obtenir_metadonnees():
    """
    Récupère les métadonnées de l'environnement d'exécution.

    Collecte des informations sur le système d'exploitation et
    l'utilisateur courant à partir des variables d'environnement
    et du module platform.

    :return: Dictionnaire contenant les clés suivantes :
        - **os** (*str*) : Nom et version du système d'exploitation (ex: ``"Windows 10"``).
        - **user** (*str*) : Nom de l'utilisateur courant, ou ``"Inconnu"`` si non trouvé.
    :rtype: dict

    :exemple:
        >>> obtenir_metadonnees()
        {"os": "Linux 5.15.0", "user": "alice"}
    """
    systeme = platform.system()
    version_os = platform.release()
    utilisateur = os.environ.get('USER') or os.environ.get('USERNAME') or "Inconnu"
    return {
        "os": f"{systeme} {version_os}",
        "user": utilisateur,
    }

def analyser(source, niveau):
    """
    Analyse les fichiers journaux (``.log``) d'un répertoire donné.

    Parcourt tous les fichiers ``.log`` du dossier ``source``, compte les
    occurrences de chaque niveau de log (ERROR, WARN, INFO), identifie
    les messages d'erreur récurrents et retourne un rapport complet
    accompagné des métadonnées système.

    :param source: Chemin vers le répertoire contenant les fichiers ``.log``.
    :type source: str ou Path
    :param niveau: Niveau de log cible (non utilisé dans l'implémentation actuelle,
                   prévu pour un filtrage futur).
    :type niveau: str

    :return: Dictionnaire contenant les clés suivantes :
        - **Nombre total de lignes analysées** (*int*) : Total de toutes les lignes lues.
        - **message recurent** (*list*) : Messages d'erreur triés par fréquence décroissante,
          sous forme de liste ``[message, occurrences]``.
        - **Comptage par niveau** (*dict*) : Nombre d'occurrences par niveau
          ``{"ERROR": int, "WARN": int, "INFO": int}``.
        - **metaDonne** (*dict*) : Métadonnées système retournées par :func:`obtenir_metadonnees`.
    :rtype: dict

    :raises Exception: Si ``source`` n'est pas un répertoire valide
                       (encapsule une ``NotADirectoryError``).

    :exemple:
        >>> rapport = analyser("/var/logs/app", "ERROR")
        >>> rapport["Comptage par niveau"]
        {"ERROR": 5, "WARN": 2, "INFO": 20}
    """
    try:
        nbrNiveau = {"ERROR": 0, "WARN": 0, "INFO": 0}
        allPhrase = 0
        nbrErrorPhrase = {}
        chemin = Path(source)
        if not chemin.is_dir():
            raise NotADirectoryError(f"Le dossier requis '{chemin}' est introuvable ou n'est pas un répertoire.")
        for item in chemin.glob('*.log'):
            with open(item, "r", encoding="utf-8") as file:
                for numero, ligne in enumerate(file, start=1):
                    if "ERROR" in ligne:
                        if(ligne.split(f"ERROR ")[1] in nbrErrorPhrase):
                            nbrErrorPhrase[ligne.split(f"ERROR ")[1]] += 1
                        else:
                            nbrErrorPhrase[ligne.split(f"ERROR ")[1]] = 1
                        nbrNiveau["ERROR"] += 1
                    if "WARN" in ligne:
                        nbrNiveau["WARN"] += 1
                    if "INFO" in ligne:
                        nbrNiveau["INFO"] += 1
                    allPhrase += 1
        return {
            "Nombre total de lignes analysées": allPhrase,
            "message recurent": tri_dict(nbrErrorPhrase),
            "Comptage par niveau": nbrNiveau,
            "metaDonne": obtenir_metadonnees()
        }
    except NotADirectoryError as e:
        raise Exception(e)