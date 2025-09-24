"""
Librairie de fonctions communes aux Workers et à la Reine
"""
import socket
from time import time
import netifaces, struct #récupération du netmask

json_data = {}

# structure de base du json
infos = {
    "queen_MAC": "",
    "queen_IP": "",
    "last_updated": "",
    "logs": [
    ]
}


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




class busyfile:
    def init_data():
        global json_data
        json_data = busyfile.charger_json()

    def charger_json():
        if JSON_FILE.exists():
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}  # si fichier vide/inexistant

    def sauvegarder_json(data):
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def ajouter_log(message):
        global json_data
        timestamp = time.strftime('%d/%m/%Y-%H:%M:%S')
        message = f"[{timestamp}] - {message}"
        json_data.setdefault("logs", []).append(message)
        busyfile.sauvegarder_json(json_data)

    def create():
        global json_data
        if not JSON_FILE.exists():
            with open(JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(infos, f, indent=4, ensure_ascii=False)
                json_data = infos.copy()
        busyfile.sauvegarder_json(json_data)

    def modify(key, value):
        global json_data
        if key in infos:
            json_data[key] = value
            busyfile.sauvegarder_json(json_data)
        else:
            print(f"Clé '{key}' non trouvée dans le JSON.")

    def update_time():
        global json_data
        busyfile.modify("last_updated", time.strftime('%d/%m/%Y-%H:%M:%S'))
