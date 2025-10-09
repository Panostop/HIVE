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
socketEcoute.setblocking(False)# empêcher le blocage pendant l'écoute


#déclaration des variables
IDWorker = os.getlogin()  # ID du worker
addrReine:str = None 
HIVELib.isAdopted = False
broadcastAddr:str = HIVELib.calcBroadcast(socketEnvoi) # calcul de l'adresse broadcast
message:bytes = None
commande:str = None





# isAdopted = True -- on est adopté, le ping s'arrête
def AttenteAdoption():
    global commande, message, addrReine, clé
    while commande != "ADPT":
        message, addrReine = HIVELib.network.Listen(socketEcoute)
        messagesplit = message.decode().split(":") # décode et découpe le message
        commande = messagesplit[0] #récupère la partie commande du message
        if commande != "ADPT":
            clé = messagesplit[1] #récupère la clé
            HIVELib.isAdopted = True
            
    
Threadlisten = threading.Thread(target=AttenteAdoption, args=(socketEcoute))
Threadlisten.start()


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

