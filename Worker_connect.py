'''
Protocole de connexion et de sécurisation du Worker
'''
import time
import os
import socket
import threading
import HIVELib


# Création des sockets
socketEnvoi = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketEcoute = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

socketEcoute.bind(('', 4173)) # prépa d'écoute sur toutes les adresses dispos sur le port HIVE

#déclaration des variables
IDWorker = os.getlogin()  # ID du worker
addrReine:str = None 
isAdopted:bool = False
broadcastAddr:str = HIVELib.calcBroadcast(socketEnvoi) # calcul de l'adresse broadcast
message:bytes = None
commande:str = None

def FREEPing():
    global IDWorker, broadcastAddr
    
    # ----- Envoi du message ----- #
    while True:
        socketEnvoi.sendto((b"FREE:"+bytes(IDWorker)), (broadcastAddr, 4173))
        time.sleep(30)
    



# si on a pas de busy.json (PARTIE MATHIAS), on ping 
threadFREEPing = threading.Thread(target=FREEPing, daemon=True) # création du thread
threadFREEPing.start()

# isAdopted = True -- on est adopté, le ping s'arrête
while commande != "ADPT":
    message, addrReine = HIVELib.Listen(socketEcoute)
    messagesplit = message.decode().split(":") # décode et découpe le message
    commande = messagesplit[0] #récupère la partie commande du message
    if commande != "ADPT":
        continue
    isAdopted = True
    clé = messagesplit[1] #récupère la clé
    
#on coupe le ping au bout d'une seconde pour bien s'assurer qu'il est dans la période d'attente
threadFREEPing.join(1) 

# on envoie un ack
socketEnvoi.sendto(b"OK", (addrReine, 4173))
time.sleep(1) 

with open(f"/home/{IDWorker}/.ssh/authorized_keys", "w") as f:
    f.write(# remplacer tout le contenu par la nouvelle clé
        'from=' + addrReine + #limitation de l'IP source
        ' no-agent-forwarding,no-port-forwarding,no-x11-forwarding' + #restrictions pour sécurité
        ' ssh-rsa ' + # type de clé
        clé + 
        "\n") 

# redémarrage du socket de récep pour vider le buffer
socketEcoute.close()
socketEcoute = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketEcoute.bind(('', 4173)) # prépa d'écoute sur toutes les adresses dispos sur le port HIVE


socketEnvoi.sendto(b"BUSY", (broadcastAddr, 4173)) #update tout le réseau

