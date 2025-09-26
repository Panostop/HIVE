'''
Génération de la clé ssh à partir de l'ID du worker et du temps depuis epoch
'''
from time import time
import os
import socket
import subprocess
import threading
import netifaces, struct #récupération du netmask
import hashlib, base64 # encodage du mot de passe
import funcs

IDWorker = os.getlogin()  # ID du worker

# Création des sockets
socketEcoute = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketEnvoi = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

socketEcoute.bind(('', 4173)) # prépa d'écoute sur toutes les adresses dispos sur le port HIVE

#globalisation des variables
addrReine = None 
isAdopted:bool = False

broadcastAddr = funcs.calcBroadcast(socketEnvoi) # calcul de l'adresse broadcast

def FREEPing():
    global isAdopted, broadcastAddr
    
    # ----- Envoi du message ----- #
    while not isAdopted:
        socketEnvoi.sendto(b"FREE", (broadcastAddr, 4173))
        time.sleep(60)
    
def ADPTListen():
    message = None
    global addrReine, isAdopted
    while message != b'ADPT':
        message, addrReine = socketEcoute.recvfrom(1024) # buffer de 1024o lu non stop
    isAdopted

def generateurMDP():
    # Génération de la clé ssh (10 caractères)
    global password, IDWorker
    
    graine = int(time.time()) #graine
    
    #j'ai aucune idée de comment, mais ca fait ce que je veux
    digest = hashlib.blake2s(f"{IDWorker}{graine}".encode()).digest()
    password = base64.urlsafe_b64encode(digest).rstrip(b'=').decode()[:10]


threadFREEPing = threading.Thread(target=FREEPing, daemon=True) # création du thread

# si on a pas de busy.json, on ping
threadFREEPing.start()
ADPTListen() # on écoute en même temps
# isAdopted = True -- on est adopté, le ping s'arrête

# on envoie un ack
socketEnvoi.sendto(b"OK", (addrReine, 4173))
# on génère le mot de passe
generateurMDP()
time.sleep(1) 
socketEnvoi.sendto(b"BUSY", (broadcastAddr, 4173)) #update tout le réseau
