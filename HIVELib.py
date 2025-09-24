"""
Librairie de fonctions communes aux Workers et à la Reine
"""
import socket
from time import time
import netifaces, struct #récupération du netmask


def calcBroadcast(socketBroadcast) -> str:
    # ----- Calcul de l'adresse braoadcast ----- #
    
    socketBroadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST) # activation du broadcast
    
    # récupération du netmask
    iface = netifaces.gateways()['default'][netifaces.AF_INET][1]  # interface par défaut
    netmask = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['netmask']
    
    # récupération de l'ip worker
    IPworker = socket.gethostbyname(socket.gethostname()) 
    
    # calcul de l'adresse de broadcast
    IPworker_int = struct.unpack("!I", socket.inet_aton(IPworker))[0] #conversions
    netmask_int = struct.unpack("!I", socket.inet_aton(netmask))[0]   #

    broadcast_int = IPworker_int | ~netmask_int & 0xFFFFFFFF
    broadcastAddr = socket.inet_ntoa(struct.pack("!I", broadcast_int))

    return broadcastAddr


def Listen(socketEcoute:socket) -> bool:
    """
    Ecoute les messages entrants
    /!\ Bloquant 
    """
    
    message = None
    message, addrSource = socketEcoute.recvfrom(1024) # buffer de 1024o bloquant en attente de réception
    

    return message, addrSource

