#bonjour
import socket
import struct
import netifaces


def calcBroadcast(socketBroadcast):
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
