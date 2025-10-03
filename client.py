#!/usr/bin/env python3
import socket
import select
import time
from pathlib import Path

BROADCAST_ADDR = "255.255.255.255"   # ou mettre l'adresse broadcast de ton sous-réseau, ex. "192.168.1.255"
PORT = 4173
isAdopted = False  # changer à True si le worker est adopté
JSON_FILE = Path("busy.json")

INTERVAL = 300                      # intervalle entre broadcasts en secondes (5 minutes = 300s)
RECV_TIMEOUT = 0 if isAdopted else INTERVAL   # combien de secondes écouter de réponses après chaque broadcast
MSG = "BUSY" if isAdopted else "FREE"


def main():
    global MSG, RECV_TIMEOUT, isAdopted

    # Déterminer le statut initial
    if JSON_FILE.exists():
        isAdopted = True
    else:
        isAdopted = False

    # Configurer la socket UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Autoriser l'envoi broadcast
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # Lier sur toutes les interfaces pour recevoir les réponses
    s.bind(('', PORT))

    try:
        while True:
            # Envoyer le broadcast
            try:
                s.sendto(MSG.encode('utf-8'), (BROADCAST_ADDR, PORT))
            except:
                print("Erreur lors de l'envoi du broadcast")

            # Écouter pendant RECV_TIMEOUT secondes pour les réponses
            end_time = time.time() + RECV_TIMEOUT

            while time.time() < end_time:
                timeout = end_time - time.time()
                if timeout <= 0:
                    break
                rlist, _, _ = select.select([s], [], [], timeout)

                if s in rlist:
                    try:
                        data, addr = s.recvfrom(4096)
                        msg = data.decode('utf-8', errors='replace').strip()

                        # Si la réponse est ACPT, envoyer le message de suivi à l'adresse source
                        if msg == "ACPT":
                            isAdopted = True


                    except Exception as e:
                        print("Erreur en lecture socket :", e)

            time.sleep(INTERVAL - RECV_TIMEOUT)

    except:
        print("\nArrêt demandé, fermeture de la socket.")
    finally:
        s.close()

if __name__ == "__main__":

    main()

    
