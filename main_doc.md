# Documentation du Module 4 : main.py

Ce fichier explique en détail le fonctionnement du point d'entrée principal de LogAnalyzer Pro.
Son rôle est d'orchestrer les 3 autres modules dans le bon ordre, de gérer les erreurs,
et d'offrir une interface en ligne de commande claire à l'utilisateur.

---

## Importation des modules

```python
import argparse
import glob
import os
import sys

from analyser import analyser
from rapport import generer_rapport
from archiver import archiver_et_nettoyer
```

| Module | Rôle |
|---|---|
| `argparse` | Gère les arguments passés en ligne de commande (`--source`, `--niveau`, etc.) |
| `glob` | Récupère la liste des fichiers `.log` présents dans le dossier source |
| `os` | Manipule les chemins de fichiers (conversion en chemins absolus) |
| `sys` | Permet d'arrêter proprement le programme avec `sys.exit(1)` en cas d'erreur fatale |
| `analyser` | Module 1 — analyse les logs et calcule les statistiques |
| `generer_rapport` | Module 2 — génère le fichier JSON horodaté |
| `archiver_et_nettoyer` | Module 3 — archive les logs et supprime les vieux rapports |

---

## Fonction `recuperer_arguments()`

```python
def recuperer_arguments():
```

### Rôle
Configure le parser d'arguments et retourne les valeurs saisies par l'utilisateur
dans le terminal. C'est cette fonction qui donne à l'outil son interface CLI.

### Arguments acceptés

| Argument | Obligatoire | Type | Défaut | Description |
|---|---|---|---|---|
| `--source` | ✅ Oui | `str` | — | Chemin vers le dossier contenant les fichiers `.log` |
| `--niveau` | ❌ Non | `str` | `ALL` | Niveau de filtrage : `ERROR`, `WARN`, `INFO` ou `ALL` |
| `--dest` | ✅ Oui | `str` | — | Dossier de destination pour les archives `.tar.gz` |
| `--retention` | ❌ Non | `int` | `30` | Nombre de jours avant suppression des anciens rapports |

### Exemple d'utilisation en ligne de commande
```bash
python main.py --source ./logs_test --dest ./backups --niveau ERROR --retention 7
```

### Détail technique
`argparse` affiche automatiquement un message d'aide si l'utilisateur oublie un argument
obligatoire ou tape `--help` :
```bash
python main.py --help
```

---

## Fonction `main()`

```python
def main():
```

### Rôle
Fonction principale qui orchestre l'ensemble du pipeline en 3 étapes séquentielles.
Chaque étape est protégée par un bloc `try/except` : si une étape échoue, le programme
affiche un message explicite et s'arrête proprement avec `sys.exit(1)`.

---

### Conversion des chemins en absolu

```python
source_absolue = os.path.abspath(args.source)
dest_absolue   = os.path.abspath(args.dest)
```

**Pourquoi ?** Un chemin relatif comme `./logs_test` dépend de l'endroit depuis lequel
on lance le script. En le convertissant en chemin absolu dès le départ
(ex: `C:\Users\...\logs_test`), on évite tous les bugs de navigation,
peu importe d'où est lancé le programme.

---

### Étape 1 — Analyse des logs

```python
resultats = analyser(source_absolue, args.niveau)
```

**Ce qui se passe :**
- Appelle la fonction `analyser()` du Module 1 avec le dossier source et le niveau de filtrage
- Récupère un dictionnaire contenant les statistiques calculées
- Construit la liste des chemins absolus de tous les fichiers `.log` trouvés via `glob`
- Si aucun fichier `.log` n'est trouvé, le programme s'arrête immédiatement

**Données extraites du résultat :**

```python
total_lignes  = resultats["Nombre total de lignes analysées"]
par_niveau    = resultats["Comptage par niveau"]
messages_tris = resultats["message recurent"]          # liste [[msg, n], ...]
top5_erreurs  = [msg for msg, _ in messages_tris[:5]]  # on garde les 5 premiers textes
```

**Exemple de sortie console :**
```
[1/3] Analyse des logs dans : C:\Users\...\logs_test
    → 62 lignes lues | ERROR=19 WARN=17 INFO=26
```

---

### Étape 2 — Génération du rapport JSON

```python
chemin_rapport = generer_rapport(
    source           = source_absolue,
    total_lignes     = total_lignes,
    par_niveau       = par_niveau,
    top5_erreurs     = top5_erreurs,
    fichiers_traites = fichiers_traites
)
```

**Ce qui se passe :**
- Appelle la fonction `generer_rapport()` du Module 2 avec toutes les données calculées à l'étape 1
- Le Module 2 crée automatiquement le dossier `rapports/` s'il n'existe pas
- Génère un fichier `rapport_YYYY-MM-DD.json` horodaté

**Exemple de sortie console :**
```
[2/3] Génération du rapport JSON...
Rapport sauvegardé avec succès : C:\Users\...\rapports\rapport_2026-03-21.json
```

**Structure du fichier JSON généré :**
```json
{
    "metadata": {
        "date": "2026-03-21 20:30:00",
        "utilisateur": "nom_utilisateur",
        "os": "Windows",
        "source": "C:\\Users\\...\\logs_test"
    },
    "statistiques": {
        "total_lignes": 62,
        "par_niveau": { "ERROR": 19, "WARN": 17, "INFO": 26 },
        "top5_erreurs": ["Échec de la connexion au serveur LDAP\n", "..."]
    },
    "fichiers_traites": [
        "C:\\Users\\...\\logs_test\\app1.log",
        "C:\\Users\\...\\logs_test\\app2.log",
        "C:\\Users\\...\\logs_test\\app3.log"
    ]
}
```

---

### Étape 3 — Archivage et nettoyage

```python
resultat_archive = archiver_et_nettoyer(
    chemin_logs   = fichiers_traites,
    destination   = dest_absolue,
    jours_fichier = args.retention
)
```

**Ce qui se passe :**
- Vérifie que l'espace disque disponible est suffisant (minimum 50 Mo)
- Compresse tous les fichiers `.log` dans une archive `backup_YYYY-MM-DD.tar.gz`
- Déplace l'archive vers le dossier `--dest`
- Supprime les rapports JSON dont l'âge dépasse le seuil `--retention`

**Exemple de sortie console :**
```
[3/3] Archivage vers 'C:\Users\...\backups' (rétention : 30 jours)...
    → Archive créée   : C:\Users\...\backups\backup_2026-03-21.tar.gz
    → Aucun rapport à supprimer (tous récents).

✅ Pipeline terminé avec succès !
```

---

## Gestion des erreurs

Chaque étape est encapsulée dans un `try/except`. En cas d'échec, le programme :
1. Affiche un message d'erreur explicite avec la cause réelle
2. Appelle `sys.exit(1)` pour signaler au système d'exploitation que le programme
   s'est terminé anormalement (code de retour `1` = erreur)

```python
except Exception as erreur:
    print(f"[ERREUR FATALE] L'analyse a planté : {erreur}")
    sys.exit(1)
```

Ce comportement est essentiel pour la planification via **Cron** : si le script plante,
Cron détecte le code de retour `1` et peut déclencher une alerte.

---

## Point d'entrée

```python
if __name__ == "__main__":
    main()
```

Cette condition garantit que `main()` n'est appelée que lorsqu'on exécute directement
`main.py`. Si un autre fichier importait `main.py`, la fonction ne se déclencherait pas
automatiquement.

---

## Schéma du pipeline

```
main.py
   │
   ├─── [1/3] analyser()          ──▶  Lit les .log, calcule les stats
   │              │
   │              ▼
   ├─── [2/3] generer_rapport()   ──▶  Écrit rapport_YYYY-MM-DD.json
   │              │
   │              ▼
   └─── [3/3] archiver_et_nettoyer() ──▶  Crée backup.tar.gz + nettoie vieux rapports
```

---

## Exemples de commandes complètes

```bash
# Lancement standard
python main.py --source ./logs_test --dest ./backups

# Filtrer uniquement les erreurs critiques
python main.py --source ./logs_test --dest ./backups --niveau ERROR

# Rétention stricte de 7 jours
python main.py --source ./logs_test --dest ./backups --retention 7

# Tous les arguments combinés
python main.py --source ./logs_test --dest ./backups --niveau WARN --retention 14
```