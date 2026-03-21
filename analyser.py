from pathlib import Path
import os
import platform
   
def tri_dict(dictionnaire):
    items = [list(item) for item in dictionnaire.items()]
    n = len(items)
    for i in range(n):
        for j in range(0, n - i - 1):
            if items[j][1] < items[j + 1][1]:
                items[j], items[j + 1] = items[j + 1], items[j]
    return items
def obtenir_metadonnees():
    systeme = platform.system()
    version_os = platform.release()
    
    utilisateur = os.environ.get('USER') or os.environ.get('USERNAME') or "Inconnu"
    
    return {
        "os": f"{systeme} {version_os}",
        "user": utilisateur,
    }

def analyser (source, niveau):
    try :
        nbrNiveau ={"ERROR":0, "WARN":0, "INFO":0}
        allPhrase =0
        nbrErrorPhrase={}
        chemin = Path(source)
        if not chemin.is_dir():
            raise NotADirectoryError(f"Le dossier requis '{chemin}' est introuvable ou n'est pas un répertoire.")
        for item in chemin.glob('*.log') :
            with open(item, "r", encoding="utf-8") as file:
                for numero, ligne in enumerate(file, start=1):   
                   
                    if "ERROR" in ligne:
                        if(ligne.split(f"ERROR ")[1] in nbrErrorPhrase):
                            nbrErrorPhrase[ligne.split(f"ERROR ")[1]]+=1
                        else :
                            nbrErrorPhrase[ligne.split(f"ERROR ")[1]] = 1                 
                        nbrNiveau["ERROR"]+=1
                    if "WARN" in ligne:
                        nbrNiveau["WARN"]+=1
                    if "INFO" in ligne:
                        nbrNiveau["INFO"]+=1
                    allPhrase+=1   
        return {
                "Nombre total de lignes analysées" : allPhrase,
                "message recurent" : tri_dict(nbrErrorPhrase),
                "Comptage par niveau" : nbrNiveau,
                "metaDonne" : obtenir_metadonnees()
            }
    except NotADirectoryError as e:
        raise Exception(e)

