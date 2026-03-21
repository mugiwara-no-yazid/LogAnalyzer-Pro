# Documentation du Module 2 : rapport.py

Ce fichier détaille étape par étape le fonctionnement du code contenu dans `rapport.py`. Son but est d'expliquer chaque choix technique comme si vous étiez débutant en Python.

## Importation des modules
```python
import json
import os
import platform
import sys
from datetime import datetime
```
- **`json`** : Permet de convertir nos listes et nos dictionnaires Python en un fichier au format texte `.json`.
- **`os`** : Sert à communiquer avec le système d'exploitation de la machine (créer des dossiers, manipuler des chemins de fichiers, lire le nom d'utilisateur de la session).
- **`platform`** : Utilisé pour détecter le système d'exploitation utilisé (Windows, Linux ou macOS).
- **`sys`** : Permet notamment d'arrêter net et proprement le programme en cas d'erreur (`sys.exit`).
- **`datetime`** : Permet d'obtenir la date et l'heure actuelle au moment exact où le code s'exécute.

## La fonction principale
```python
def generer_rapport(source, total_lignes, par_niveau, top5_erreurs, fichiers_traites):
```
Cette fonction prend 5 arguments en entrée. Ce sont les données qui auront été calculées par le **Module 1** (l'analyseur) et que l'on veut figer dans le temps via le fichier JSON.

### Bloc try/except et horodatage
```python
    try:
        maintenant = datetime.now()
        date_fichier = maintenant.strftime("%Y-%m-%d")
        date_rapport = maintenant.strftime("%Y-%m-%d %H:%M:%S")
```
- **`try :`** On place tout le code dans ce bloc. S'il y a la moindre erreur (ex: pas le droit d'écrire sur le disque dur), le programme n'explosera pas salement. Il sautera directement dans le bloc `except` plus bas.
- **`strftime(...)`** : Permet de donner le format qu'on veut à notre date. `%Y` c'est l'année sur 4 chiffres, `%m` le mois, etc. On crée deux formats différents : l'un pour nommer le fichier sans espaces, l'autre pour écrire la date précise dans le document.

### Métadonnées du système
```python
        utilisateur = os.environ.get("USER") or os.environ.get("USERNAME") or "Inconnu"
        systeme_os = platform.system()
```
- Selon si vous êtes sur Linux/Mac (`USER`) ou sur Windows (`USERNAME`), la variable d'environnement qui contient votre nom change. C'est pourquoi on utilise un petit `or` (le premier qui existe est pris).
- `platform.system()` va répondre un mot clair (`Windows`, `Linux` ou `Darwin`).

### Construction du dictionnaire
```python
        donnees_rapport = {
            "metadata": { ... },
            "statistiques": { ... },
            "fichiers_traites": fichiers_traites
        }
```
Nous respectons exactement la consigne du TP en imbriquant des dictionnaires les uns dans les autres (avec des accolades `{}`).

### Chemins Absolus (Obligatoire)
```python
        chemin_fichier_actuel = os.path.abspath(__file__)
        dossier_actuel = os.path.dirname(chemin_fichier_actuel)
        dossier_rapports = os.path.join(dossier_actuel, "rapports")
```
- **`__file__`** : C'est une variable magique Python qui contient le chemin de CE fichier de code (`rapport.py`).
- **`os.path.abspath()`** : Permet de transformer "rapport.py" en un chemin complet à partir de la racine du disque (par ex: `C:\Users\...\rapport.py`). Cela évite énormément de bugs de navigation relatifs !
- **`os.path.dirname()`** : Supprime le mot "rapport.py" de la chaîne pour ne garder que le dossier parent.
- **`os.path.join(...)`** : Assemble les chemins très proprement sans s'inquiéter du sens des slashs (`\` ou `/`).

### Création du dossier et du fichier
```python
        if not os.path.exists(dossier_rapports):
            os.makedirs(dossier_rapports)

        nom_fichier = f"rapport_{date_fichier}.json"
        chemin_complet_fichier = os.path.join(dossier_rapports, nom_fichier)
```
- `os.path.exists()` vérifie si le dossier `rapports` existe déjà. Si ce n'est pas le cas (`not`), on le crée avec `os.makedirs()`. 

### Écriture du JSON sur le disque
```python
        with open(chemin_complet_fichier, "w", encoding="utf-8") as fichier:
            json.dump(donnees_rapport, fichier, indent=4)
```
- **`with open(..., "w")`** : Ouvre le fichier en mode écriture (`w` = write). Il sera créé s'il n'existait pas, et écrasé s'il existait déjà. Le `with` est génial car il ferme automatiquement le fichier même s'il y a un plantage. C'est très propre.
- **`encoding="utf-8"`** : Assure que nos accents (é, à, ù...) ne soient pas corrompus.
- **`json.dump(...)`** : Convertit notre gros dictionnaire Python en texte reconnu par JSON, et écrit ça en direct dans notre fichier.
- **`indent=4`** : Rend le fichier beaucoup plus lisible pour des yeux humains en ajoutant des sauts de ligne et des indentations (espaces).

### Gestion d'erreurs
```python
    except Exception as erreur:
        print(f"Une erreur s'est produite lors de la génération du rapport : {erreur}")
        sys.exit(1)
```
- Si quoi que ce soit rate, on est attrapé dans l'Exception. On print un message contenant la vraie raison (`erreur`) puis on alerte le système d'exploitation avec le code `1` (qui veut dire: "Il y a un problème, je ne suis pas allé au bout normalement !").
