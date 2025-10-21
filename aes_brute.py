# -*- coding: utf-8 -*-

import pyAesCrypt
import argparse
import sys
import os
import threading
import queue
from datetime import datetime
import uuid

# --- Bannière ---
def print_banner():
    """ Affiche la bannière du script. """
    print(r"""
    
__________          _____                __________                __
\______   \___.__. /  _  \   ____   _____\______   \_______ __ ___/  |_  ____
|     ___<   |  |/  /_\  \_/ __ \ /  ___/|    |  _/\_  __ \  |  \   __\/ __ \
|    |    \___  /    |    \  ___/ \___ \ |    |   \ |  | \/  |  /|  | \  ___/
|____|    / ____\____|__  /\___  >____  >|______  / |__|  |____/ |__|  \___  >
       \/            \/     \/     \/        \/                         \/ 
                
               Un outil par : Cantin L. aka Valak
              PyAesBrute - Multi-Threaded Decrypter
                  Version : 01 - 21 - 10 - 2025
              
    """)
                
# --- Variables Globales ---
password_queue = queue.Queue(maxsize=5000) 
password_found = threading.Event()
counter_lock = threading.Lock()
attempt_counter = 0
# ----------------------------------------

def producer(wordlist_file, num_threads):
    """
    Thread "Producteur" : lit la wordlist et remplit la file d'attente.
    """
    global password_queue, password_found
    
    print(f"[+] Démarrage du Producteur : Lecture de '{wordlist_file}'...")
    try:
        with open(wordlist_file, "r", encoding="latin-1") as wl:
            for line in wl:
                if password_found.is_set():
                    break
                
                # 'put' bloque si la file est pleine, régulant la RAM
                password_queue.put(line.strip())
                
    except FileNotFoundError:
        print(f"[-] Erreur Producteur : Wordlist non trouvée à '{wordlist_file}'")
        password_found.set()
    except Exception as e:
        print(f"[-] Erreur Producteur : {e}")
        password_found.set()

    print("[+] Producteur : Lecture terminée. Envoi des signaux d'arrêt aux workers...")
    for _ in range(num_threads):
        password_queue.put(None) # 'None' est la "pilule" d'arrêt

def worker(encrypted_file, final_decrypted_file):
    """
    Fonction "Consommateur" exécutée par chaque thread.
    """
    global attempt_counter, password_found, password_queue, counter_lock
    bufferSize = 64 * 1024

    while True:
        password = password_queue.get() 

        # --- Logique d'arrêt ---
        # 1. Le thread s'arrête s'il reçoit 'None'
        if password is None:
            return 

        # 2. Si un autre thread a trouvé, on "draine" la file :
        # on s'arrête de travailler mais on continue de vider la file
        # pour débloquer le producteur.
        if password_found.is_set():
            continue
        # --- Fin Logique d'arrêt ---

        current_attempt = 0
        with counter_lock:
            attempt_counter += 1
            current_attempt = attempt_counter
        
        print(f"\r[*] Tentative #{current_attempt}: Essai du mot de passe '{password}'...          ", end="")

        temp_decrypted_file = f"decrypted_tmp_{uuid.uuid4()}"
        
        try:
            pyAesCrypt.decryptFile(
                encrypted_file,
                temp_decrypted_file, 
                password,
                bufferSize
            )

            # --- SUCCÈS ---
            password_found.set()
            
            try:
                os.rename(temp_decrypted_file, final_decrypted_file)
            except OSError as e:
                print(f"\n[-] ERREUR critique : Impossible de renommer le fichier. Le bon fichier est '{temp_decrypted_file}'. Erreur: {e}")

            print(f"\n\n[+] SUCCÈS ! Mot de passe trouvé : {password}")
            print(f"[+] Fichier déchiffré avec succès : '{final_decrypted_file}'")

        except ValueError:
            # Mot de passe incorrect
            pass 
        except Exception as e:
            with counter_lock:
                 print(f"\n[-] Erreur sur le mot de passe '{password}': {e}")
        finally:
            # Nettoyage du fichier temporaire
            if os.path.exists(temp_decrypted_file):
                try:
                    os.remove(temp_decrypted_file)
                except OSError:
                    pass

def main():
    """
    Fonction principale pour coordonner la tentative de déchiffrement.
    """
    
    parser = argparse.ArgumentParser(
        description="""
        PyAesBrute: Lance une attaque par dictionnaire multithread sur un fichier 
        chiffré avec pyAesCrypt (.aes).
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    file_group = parser.add_argument_group('Arguments de Fichier (Obligatoires)')
    file_group.add_argument("-f", "--file", 
                            dest="file", 
                            help="Chemin vers le fichier .aes que vous voulez déchiffrer.", 
                            required=True)
    file_group.add_argument("-w", "--wordlist", 
                            dest="wordlist", 
                            help="Chemin vers la liste de mots de passe (ex: rockyou.txt).", 
                            required=True)

    options_group = parser.add_argument_group('Arguments Optionnels')
    options_group.add_argument("-t", "--threads", 
                               dest="threads", 
                               help="Nombre de threads à utiliser. (Défaut: nombre de cœurs CPU)", 
                               type=int, 
                               default=os.cpu_count())
    options_group.add_argument("-o", "--output",
                               dest="output_file",
                               help="Nom du fichier déchiffré. (Défaut: 'decrypted_file')",
                               default="decrypted_file")
    
    args = parser.parse_args()
    print_banner()

    encrypted_file = args.file
    wordlist_file = args.wordlist
    num_threads = args.threads or 4 
    final_decrypted_file = args.output_file
    
    # --- Validation des fichiers ---
    if not os.path.exists(encrypted_file):
        print(f"[-] Erreur : Fichier chiffré non trouvé -> '{encrypted_file}'")
        sys.exit(1)
    if not os.path.exists(wordlist_file):
        print(f"[-] Erreur : Wordlist non trouvée -> '{wordlist_file}'")
        sys.exit(1)

    if os.path.exists(final_decrypted_file):
        print(f"[!] Attention : Le fichier de sortie '{final_decrypted_file}' existe déjà et sera écrasé en cas de succès.")
        try:
            input("    Appuyez sur Entrée pour continuer, ou Ctrl+C pour annuler...")
        except KeyboardInterrupt:
            print("\n[!] Opération annulée par l'utilisateur.")
            sys.exit(0)

    # --- Logique principale ---
    try:
        start_time = datetime.now()
        print(f"\n[+] Démarrage de l'attaque sur {encrypted_file} à {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[+] Utilisation de {num_threads} threads (Consommateurs).")
        
        producer_thread = threading.Thread(target=producer, args=(wordlist_file, num_threads))
        producer_thread.daemon = True
        producer_thread.start()
        
        worker_threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=worker, args=(
                encrypted_file,
                final_decrypted_file 
            ))
            t.daemon = True
            t.start()
            worker_threads.append(t)
            
        # --- CORRECTION DU BUG ---
        # On attend d'abord que le producteur ait fini de lire le fichier
        # et d'envoyer tous les signaux d'arrêt.
        producer_thread.join()
        
        # Ensuite, on attend que tous les workers aient fini de traiter
        # la file d'attente (y compris les signaux d'arrêt).
        for t in worker_threads:
            t.join()
        # --- FIN CORRECTION ---

        print() 
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        if not password_found.is_set():
            print(f"\n[-] ÉCHEC. Tous les mots de passe ont été essayés.")
        
        print(f"[+] Terminé en {duration.total_seconds():.2f} secondes.")
        
        # Nettoyage final
        for item in os.listdir("."):
            if item.startswith("decrypted_tmp_"):
                try:
                    os.remove(item)
                except OSError:
                    pass

    except KeyboardInterrupt:
        print("\n\n[!] Attaque arrêtée par l'utilisateur.")
        password_found.set()
        for item in os.listdir("."):
            if item.startswith("decrypted_tmp_"):
                try:
                    os.remove(item)
                except OSError:
                    pass
        sys.exit(0)
    except Exception as e:
        print(f"\n[-] Une erreur inattendue est survenue : {e}")

if __name__ == "__main__":
    main()
