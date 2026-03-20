#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module 2 : Génération du rapport JSON
Ce module prend les données analysées par le module 1 et génère un fichier JSON.
"""

import json
import os
import platform
from datetime import datetime

def generer_rapport(source, total_lignes, par_niveau, top5_erreurs, fichiers_traites):
    """
    Crée un fichier JSON contenant le rapport de l'analyse des logs.
    """
    try:
        # Obtenir la date et l'heure actuelles
        maintenant = datetime.now()
        
        # Formater la date pour le nom du fichier (YYYY-MM-DD)
        date_fichier = maintenant.strftime("%Y-%m-%d")
        
        # Formater la date et l'heure pour le contenu du rapport
        date_rapport = maintenant.strftime("%Y-%m-%d %H:%M:%S")
        
        # Trouver le nom de l'utilisateur (ça dépend si on est sur Windows ou Linux/Mac)
        utilisateur = os.environ.get("USER") or os.environ.get("USERNAME") or "Inconnu"
        
        # Trouver le système d'exploitation
        systeme_os = platform.system()
        
        # Préparer le dictionnaire qui va devenir notre fichier JSON
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
        
        # Trouver le chemin de ce fichier python (rapport.py)
        chemin_fichier_actuel = os.path.abspath(__file__)
        
        # Trouver le dossier où se trouve ce fichier (le dossier loganalyzer)
        dossier_actuel = os.path.dirname(chemin_fichier_actuel)
        
        # Créer le chemin pour le dossier "rapports"
        dossier_rapports = os.path.join(dossier_actuel, "rapports")
        
        # Créer le dossier "rapports" s'il n'existe pas déjà
        if not os.path.exists(dossier_rapports):
            os.makedirs(dossier_rapports)
        
        # Créer le nom du fichier avec la date
        nom_fichier = f"rapport_{date_fichier}.json"
        
        # Créer le chemin complet pour le nouveau fichier JSON
        chemin_complet_fichier = os.path.join(dossier_rapports, nom_fichier)
        
        # Ouvrir le fichier en mode écriture ("w") et écrire les données en JSON
        with open(chemin_complet_fichier, "w", encoding="utf-8") as fichier:
            # json.dump écrit le dictionnaire dans le fichier. indent=4 rend le fichier facile à lire.
            json.dump(donnees_rapport, fichier, indent=4)
            
        print(f"Rapport sauvegardé avec succès : {chemin_complet_fichier}")
        return chemin_complet_fichier
        
    except Exception as erreur:
        print(f"Une erreur s'est produite lors de la génération du rapport : {erreur}")
        # On quitte le programme avec une erreur
        import sys
        sys.exit(1)

# Petit test pour voir si la fonction marche (cette partie ne s'exécutera que si on lance rapport.py directement)
if __name__ == "__main__":
    # Données bidon pour tester
    source_test = "/chemin/vers/logs"
    lignes_test = 150
    niveaux_test = {"ERROR": 10, "WARN": 40, "INFO": 100}
    erreurs_test = ["Erreur 1", "Erreur 2", "Erreur 3"]
    fichiers_test = ["app1.log", "app2.log"]
    
    # Appel de la fonction pour le test
    generer_rapport(source_test, lignes_test, niveaux_test, erreurs_test, fichiers_test)
