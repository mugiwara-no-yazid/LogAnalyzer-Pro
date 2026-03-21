#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import glob
import os
import sys

from analyser import analyser
from rapport import generer_rapport
from archiver import archiver_et_nettoyer


def recuperer_arguments():

    parser = argparse.ArgumentParser(
        description="LogAnalyzer Pro — Pipeline d'analyse et d'archivage de logs"
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Chemin vers le dossier contenant les fichiers .log à analyser"
    )
    parser.add_argument(
        "--niveau",
        choices=["ERROR", "WARN", "INFO", "ALL"],
        default="ALL",
        help="Niveau de criticité à filtrer (défaut : ALL)"
    )
    parser.add_argument(
        "--dest",
        required=True,
        help="Dossier de destination pour stocker les archives .tar.gz"
    )
    parser.add_argument(
        "--retention",
        type=int,
        default=30,
        help="Nombre de jours avant suppression des anciens rapports (défaut : 30)"
    )
    return parser.parse_args()


def main():
    """
    Orchestre les 3 modules dans l'ordre : analyse → rapport → archivage.
    Chaque étape est protégée par un try/except, le script s'arrête proprement en cas de pépin.
    """

    
    args = recuperer_arguments()
    source_absolue = os.path.abspath(args.source)
    dest_absolue = os.path.abspath(args.dest)

    print(f"\n[1/3] Analyse des logs dans : {source_absolue}")
    try:
        resultats = analyser(source_absolue, args.niveau)
    except Exception as erreur:
        print(f"[ERREUR FATALE] L'analyse a planté : {erreur}")
        sys.exit(1)

    # On récupère les chemins absolus de tous les .log pour les passer aux modules suivants
    fichiers_traites = [
        os.path.abspath(f)
        for f in glob.glob(os.path.join(source_absolue, "*.log"))
    ]

    if not fichiers_traites:
        print("[ERREUR FATALE] Aucun fichier .log trouvé dans le dossier source.")
        sys.exit(1)

    # On mappe les clés renvoyées par analyser.py vers ce qu'attend rapport.py
    total_lignes  = resultats["Nombre total de lignes analysées"]
    par_niveau    = resultats["Comptage par niveau"]
    messages_tris = resultats["message recurent"]          # liste [[msg, n], ...]
    top5_erreurs  = [msg for msg, _ in messages_tris[:5]]  # on garde seulement les textes

    print(f"    → {total_lignes} lignes lues | "
          f"ERROR={par_niveau['ERROR']} WARN={par_niveau['WARN']} INFO={par_niveau['INFO']}")

    # ── ÉTAPE 2 : Génération du rapport JSON ─────────────────────────────────
    print("\n[2/3] Génération du rapport JSON...")
    try:
        chemin_rapport = generer_rapport(
            source         = source_absolue,
            total_lignes   = total_lignes,
            par_niveau     = par_niveau,
            top5_erreurs   = top5_erreurs,
            fichiers_traites = fichiers_traites
        )
    except Exception as erreur:
        print(f"[ERREUR FATALE] La génération du rapport a planté : {erreur}")
        sys.exit(1)

    # ── ÉTAPE 3 : Archivage des logs + nettoyage des vieux rapports ──────────
    print(f"\n[3/3] Archivage vers '{dest_absolue}' (rétention : {args.retention} jours)...")
    try:
        resultat_archive = archiver_et_nettoyer(
            chemin_logs  = fichiers_traites,
            destination  = dest_absolue,
            jours_fichier = args.retention
        )
        print(f"    → Archive créée   : {resultat_archive['archive']}")
        rapports_supprimes = resultat_archive["rapports_supprimes"]
        if rapports_supprimes:
            print(f"    → Rapports supprimés ({len(rapports_supprimes)}) : {rapports_supprimes}")
        else:
            print("    → Aucun rapport à supprimer (tous récents).")
    except Exception as erreur:
        print(f"[ERREUR FATALE] L'archivage a planté : {erreur}")
        sys.exit(1)

    print("\n✅ Pipeline terminé avec succès !\n")


if __name__ == "__main__":
    main()