'''
Protocole de connexion et de sécurisation du Worker
'''
from time import time
import os
import socket
import subprocess
import threading
import HIVELib


# Création des sockets
socketEcoute = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketEnvoi = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

socketEcoute.bind(('', 4173)) # prépa d'écoute sur toutes les adresses dispos sur le port HIVE

#déclaration des variables
IDWorker = os.getlogin()  # ID du worker
addrReine:str = None 
isAdopted:bool = False
broadcastAddr:str = HIVELib.calcBroadcast(socketEnvoi) # calcul de l'adresse broadcast

def FREEPing():
    global isAdopted, broadcastAddr
    
    # ----- Envoi du message ----- #
    while not isAdopted:
        socketEnvoi.sendto(b"FREE", (broadcastAddr, 4173))
        time.sleep(60)
    


# si on a pas de busy.json (PARTIE MATHIAS), on ping 
threadFREEPing = threading.Thread(target=FREEPing, daemon=True) # création du thread
threadFREEPing.start()

# isAdopted = True -- on est adopté, le ping s'arrête
isAdopted, addrReine = HIVELib.Listen(socketEcoute, "ADPT", addrReine)
threadFREEPing.join() #on coupe le ping

# on envoie un ack
socketEnvoi.sendto(b"OK", (addrReine, 4173))
# on génère le mot de passe
password = HIVELib.generateurMDP(IDWorker)
time.sleep(1) 
socketEnvoi.sendto(b"BUSY", (broadcastAddr, 4173)) #update tout le réseau

