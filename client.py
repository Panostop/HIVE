#!/usr/bin/env python3
import socket
import select
import time
from pathlib import Path
import libclient
import os

BROADCAST_ADDR = "255.255.255.255"   # ou mettre l'adresse broadcast de ton sous-réseau, ex. "192.168.1.255"
PORT = 4173
JSON_FILE = Path("busy.json")

INTERVAL = 300                      # intervalle entre broadcasts en secondes (5 minutes = 300s)
RECV_TIMEOUT = 0 if libclient.isAdopted else INTERVAL   # combien de secondes écouter de réponses après chaque broadcast
MSG = "BUSY" if libclient.isAdopted else "FREE"


def main():
    global MSG, RECV_TIMEOUT

    # Déterminer le statut initial
    if JSON_FILE.exists():
        libclient.isAdopted = True
        if libclient.divers.is_too_old():
            libclient.isAdopted = False
            os.remove(JSON_FILE)
            json_data = {}

    else:
        libclient.isAdopted = False





    # Configurer la socket UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Autoriser l'envoi broadcast
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # Lier sur toutes les interfaces pour recevoir les réponses
    s.bind(('', PORT))

    try:
        pass

    except:
        print("\nArrêt demandé, fermeture de la socket.")
    finally:
        s.close()

if __name__ == "__main__":

    main()

    
