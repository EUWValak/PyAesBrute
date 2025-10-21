# PyAesBrute
PyAesBrute est un outil en ligne de commande Python, multithreadé et optimisé, pour trouver le mot de passe d'un fichier chiffré avec [pyAesCrypt](https://pypi.org/project/pyaescrypt/) (format `.aes`).

Il utilise une attaque par dictionnaire et un modèle producteur/consommateur pour une performance maximale et une utilisation minimale de la RAM, même avec des listes de mots de passe de plusieurs gigaoctets.

## ⚠️ Avertissement Éthique

Cet outil est conçu à des fins éducatives, pour l'audit de sécurité et la récupération de mots de passe personnels. L'auteur n'est pas responsable d'une utilisation malveillante. N'utilisez **jamais** cet outil sur des fichiers qui ne vous appartiennent pas sans autorisation explicite.

## Fonctionnalités

* **Multithreading** : Utilise tous les cœurs de votre CPU pour une vitesse maximale.
* **Faible utilisation RAM** : Ne charge pas la wordlist en mémoire. Il la "streame", ce qui lui permet de gérer des fichiers de plusieurs Go sans saturer la RAM.
* **Démarrage instantané** : L'attaque commence immédiatement, sans temps de chargement.
* **Propre** : Gère les interruptions (Ctrl+C) et nettoie les fichiers temporaires.
* **Simple d'utilisation** : Interface en ligne de commande claire.

## Installation

1.  Clonez ce dépôt :
    ```bash
    git clone https://github.com/EUWVeNoM/PyAesBrute
    cd PyAesBrute
    ```
2. Créez un environnement virtuel :
    ```bash
    python3 -m venv .venv
    ```
3. Activez l'environnement virtuel :
    ```bash
    source .venv/bin/activate
    ```
4.  Installez la seule dépendance (pyAesCrypt) :
    ```bash
    pip install -r requirements.txt
    ```

## Utilisation

L'utilisation est simple. Vous devez fournir le fichier chiffré (`-f`) et la wordlist (`-w`).

```bash
python3 aes_brute.py -h

usage: aes_brute.py [-h] -f FILE -w WORDLIST [-t THREADS] [-o OUTPUT_FILE]

PyAesBrute: Lance une attaque par dictionnaire multithread sur un fichier
chiffré avec pyAesCrypt (.aes).

Arguments de Fichier (Obligatoires):
  -f FILE, --file FILE  Chemin vers le fichier .aes que vous voulez déchiffrer.
  -w WORDLIST, --wordlist WORDLIST
                        Chemin vers la liste de mots de passe (ex: rockyou.txt).

Arguments Optionnels:
  -t THREADS, --threads THREADS
                        Nombre de threads à utiliser. (Défaut: nombre de cœurs CPU)
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        Nom du fichier déchiffré. (Défaut: 'decrypted_file')
```

## Exemple

Pour attaquer un fichier nommé secret.zip.aes avec rockyou.txt en utilisant 12 threads et en sauvegardant le résultat sous secret_dechiffre.zip :


```bash
python3 aes_brute.py -f secret.zip.aes -w /usr/share/wordlists/rockyou.txt -t 12 -o secret_dechiffre.zip
```
