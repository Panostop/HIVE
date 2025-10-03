from prettytable import PrettyTable 
import socket
import threading
import urllib
import requests
import psutil
import ipaddress
import time
import select
import os

workers_list = []
workers_states = []
active_workers = []

PORT = 4173

class threads:
    class thread_udp_listener():


        def udp_listener():
            global workers_list, workers_states

            host = "0.0.0.0"   # écoute sur toutes les interfaces réseau
            port = 4173        # port choisi

            # Créer un socket UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((host, port))

            print(f"Écoute UDP sur {host}:{port}... (Ctrl+C pour arrêter)")

            while True:
                data, addr = sock.recvfrom(1024)  # buffer de 1024 octets
                print(f"[{addr[0]}:{addr[1]}] -> {data.decode(errors='ignore')}")

                if addr[0] not in workers_list:
                    workers_list.append(addr[0])
                    print(f"Nouveau worker détecté : {addr[0]}")

                position = workers_list.index(addr[0])
                workers_states[position] = data.decode(errors='ignore')


        udp_listener_stop_event = threading.Event()
        thread_udp_listener = threading.Thread(target=udp_listener, args=(udp_listener_stop_event,))

        def start():
            threads.thread_udp_listener.start()

        def stop():
            threads.thread_udp_listener.udp_listener_stop_event.set()
            threads.thread_udp_listener.join()





class Network:
    def check_internet():
        try:
            urllib.request.urlopen('http://google.com', timeout=1)
            return True
        except:
            return False
    
    def get_local_ip():
        try:
            # se connecte à une IP publique (Google DNS), sans envoyer de paquets
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip   #renvoit l'IP locale ex: 192.168.0.1
        except Exception:
            return "Inconnue"
        
    def get_public_ip():
        try:
            # requête à un service web pour obtenir l'IP publique
            return requests.get("https://api.ipify.org").text
        except Exception:
            return "Inconnue"
        
    def get_eth_info(searched):
        interfaces = psutil.net_if_addrs()
        for iface, addrs in interfaces.items():
            for addr in addrs:
                if addr.family.name == "AF_INET":  # IPv4
                    if (searched in addr.address):
                        return addr.address, addr.netmask
                    
        return None, None
                                     
    def get_wlan_info(searched):
        interfaces = psutil.net_if_addrs()
        for iface, addrs in interfaces.items():
            for addr in addrs:
                if addr.family.name == "AF_INET":  # IPv4
                    if (searched in addr.address):
                        return addr.address, addr.netmask
                    
        return None, None
                    
    def calculate_broadcast_adress(ip, masque):
        cidr = f"{ip}/{masque}"
        reseau = ipaddress.ip_network(cidr, strict=False)
        #print(calculer_broadcast_ip_masque("192.168.1.42", "255.255.255.0"))
        return str(reseau.broadcast_address)

    def init_network():
        global BROADCAST_ADDR, LOCAL_IP
        print("Initialisation du réseau...")
        if Network.check_internet():
            LOCAL_IP = Network.get_local_ip()
            print(f"reseau détecté, IP locale : {LOCAL_IP}")
            if LOCAL_IP != "Inconnue":
                ip, masque = Network.get_eth_info(LOCAL_IP)
                if ip and masque:
                    BROADCAST_ADDR = Network.calculate_broadcast_adress(ip, masque)
                    print(f"Adresse de broadcast calculée (Ethernet) : {BROADCAST_ADDR}")
                    return True
                else:
                    ip, masque = Network.get_wlan_info(LOCAL_IP)
                    if ip and masque:
                        BROADCAST_ADDR = Network.calculate_broadcast_adress(ip, masque)
                        print(f"Adresse de broadcast calculée (WiFi) : {BROADCAST_ADDR}")
                        return True
                    else:
                        BROADCAST_ADDR = ""
                        print("Impossible de déterminer l'interface réseau.")
                        return False
            else:
                BROADCAST_ADDR = ""
                print("Impossible de déterminer l'IP locale.")
                return False
        else:
            LOCAL_IP = "Inconnue"
            BROADCAST_ADDR = ""
            print("Pas de connexion internet détectée.")
            return False
    


        
    def broadcast_scan():
        global PORT

        # Configurer la socket UDP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Autoriser l'envoi broadcast
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Lier sur toutes les interfaces pour recevoir les réponses
        s.bind(('', PORT))

        try:
            
                # Envoyer le broadcast
                try:
                    s.sendto("STAT".encode('utf-8'), (BROADCAST_ADDR, PORT))
                except:
                    print("Erreur lors de l'envoi du broadcast")

                print("scanning..., please wait")

                # Écouter pendant 60 secondes pour les réponses
                end_time = time.time() + 60

                while time.time() < end_time:
                    timeout = end_time - time.time()
                    if timeout <= 0:
                        break

                    rlist, _, _ = select.select([s], [], [], timeout)
                    if s in rlist:
                        try:
                            data, addr = s.recvfrom(4096)
                            msg = data.decode('utf-8', errors='replace').strip()

                            #format reponse BUSY ou FREE
                            if msg in ["BUSY", "FREE"]:
                                if addr[0] not in active_workers:
                                    active_workers.append(addr[0])
                                    workers_states.append(msg)
                                    print(f"Worker actif détecté : {addr[0]} - État : {msg}")

                                position = active_workers.index(addr[0])
                                workers_states[position] = msg                            

                        except Exception as e:
                            print("Erreur en lecture des reponses :", e)


        except:
                print("\nArrêt demandé, fermeture de la socket.")
        finally:
                s.close()















def create_table(headers, row_number, data, filter=None):
    #use ["Name", "City", "Class", "Percentage"] for headers

    if len(headers) != 2:
        print("different argument number")
        return
    
    # specify the Column Names while initializing the Table 
    table = PrettyTable(headers) 

    for i in range(row_number):
        try:
            table.add_row([data[0][i], data[1][i]]) 
        except:
            pass

    print(table)



