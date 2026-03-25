#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import platform
import sys
from datetime import datetime


def generer_rapport(source, total_lignes, par_niveau, top5_erreurs, fichiers_traites):
    """
    Génère et sauvegarde un rapport d'analyse de logs au format JSON.

    Collecte les métadonnées système (date, utilisateur, OS), structure
    les statistiques fournies et écrit le tout dans un fichier
    ``rapport_YYYY-MM-DD.json`` dans le sous-dossier ``rapports/``
    situé au même niveau que le script.

    :param source: Chemin du dossier source des fichiers journaux analysés.
    :type source: str
    :param total_lignes: Nombre total de lignes lues dans tous les fichiers.
    :type total_lignes: int
    :param par_niveau: Comptage des occurrences par niveau de log.

        Exemple::

            {"ERROR": 12, "WARN": 5, "INFO": 87}

    :type par_niveau: dict[str, int]
    :param top5_erreurs: Liste des messages d'erreur les plus fréquents,
                         triés par ordre décroissant d'occurrences.

        Exemple::

            [["connexion refusée\\n", 8], ["timeout\\n", 3]]

    :type top5_erreurs: list[list]
    :param fichiers_traites: Liste des chemins des fichiers ``.log`` traités.
    :type fichiers_traites: list[str]

    :return: Chemin absolu du fichier rapport généré.
    :rtype: str

    :raises SystemExit: Quitte le programme avec le code ``1`` si une erreur
                        survient lors de la création du dossier ou de l'écriture
                        du fichier.

    :exemple:
        >>> generer_rapport(
        ...     source="/var/logs/app",
        ...     total_lignes=500,
        ...     par_niveau={"ERROR": 10, "WARN": 20, "INFO": 470},
        ...     top5_erreurs=[["timeout\\n", 7], ["null pointer\\n", 3]],
        ...     fichiers_traites=["/var/logs/app/app.log"]
        ... )
        Rapport sauvegardé avec succès : /projet/rapports/rapport_2024-06-15.json
        '/projet/rapports/rapport_2024-06-15.json'

    .. note::
        Si un rapport du même jour existe déjà, il sera **écrasé** sans avertissement.
    """
    try:
        maintenant = datetime.now()
        date_fichier = maintenant.strftime("%Y-%m-%d")
        date_rapport = maintenant.strftime("%Y-%m-%d %H:%M:%S")

        utilisateur = os.environ.get("USER") or os.environ.get("USERNAME") or "Inconnu"
        systeme_os = platform.system()

        donnees_rapport = {
            "metadata": {
                "date": date_rapport,
                "utilisateur": utilisateur,
                "os": systeme_os,
                "source": source
            },
            "statistiques": {
                "total_lignes": total_lignes,
                "par_niveau": par_niveau,
                "top5_erreurs": top5_erreurs
            },
            "fichiers_traites": fichiers_traites
        }

        chemin_fichier_actuel = os.path.abspath(__file__)
        dossier_actuel = os.path.dirname(chemin_fichier_actuel)
        dossier_rapports = os.path.join(dossier_actuel, "rapports")

        if not os.path.exists(dossier_rapports):
            os.makedirs(dossier_rapports)

        nom_fichier = f"rapport_{date_fichier}.json"
        chemin_complet_fichier = os.path.join(dossier_rapports, nom_fichier)

        with open(chemin_complet_fichier, "w", encoding="utf-8") as fichier:
            json.dump(donnees_rapport, fichier, indent=4)

        print(f"Rapport sauvegardé avec succès : {chemin_complet_fichier}")
        return chemin_complet_fichier

    except Exception as erreur:
        print(f"Une erreur s'est produite lors de la génération du rapport : {erreur}")
        sys.exit(1)