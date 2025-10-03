import socket
import requests
import urllib
import psutil
import ipaddress
import time
import json
import os
from pathlib import Path
from datetime import datetime
import threading
import hashlib, base64 # encodage du mot de passe
import select
import subprocess

isAdopted = False  # changer à True si le worker est adopté

json_data = {}

INTERVAL = 300                      # intervalle entre broadcasts en secondes (5 minutes = 300s)
RECV_TIMEOUT = 0 if isAdopted else INTERVAL   # combien de secondes écouter de réponses après chaque broadcast
MSG = "BUSY" if isAdopted else "FREE"

BROADCAST_ADDR = ""
LOCAL_IP = ""

JSON_FILE = Path("busy.json")
PORT = 4173
QUEEN_IP = json_data["queen_IP"] if os.path.exists(JSON_FILE) else ""


# structure de base du json
infos = {
    "queen_MAC": "",
    "queen_IP": "",
    "last_updated": "",
    "logs": [
    ]
}



    
                
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




class threads:

    class inactivity_timer:

        def inactivity_timer(inactivity_timer_stop_event, inactivity_timer_reset_event):
            global isAdopted, json_data

            # Configurer la socket UDP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Autoriser l'envoi broadcast
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            # Lier sur toutes les interfaces pour recevoir les réponses
            s.bind(('', PORT))

            start = time.time()
            while not inactivity_timer_stop_event.is_set():
                if inactivity_timer_reset_event.is_set():  # si on demande un reset
                    start = time.time()
                    inactivity_timer_reset_event.clear()   # on efface le signal pour repartir propre
        
                elapsed = time.time() - start

                if not (elapsed % 300):
                    try:
                        s.sendto(MSG.encode('utf-8'), (QUEEN_IP, PORT))
                    except:
                        print("Erreur lors du ping")
                        os.remove(JSON_FILE)
                        inactivity_timer_stop_event.set()

                if elapsed >= (3 * 3600):  # 3 heures
                    global json_data
                    if os.path.exists(JSON_FILE):
                        os.remove(JSON_FILE)
                    json_data = {}
                    isAdopted = False
                    inactivity_timer_stop_event.set()
                time.sleep(0.2)

        def ssh_viewer():
            # utilise ausearch pour filtrer les commandes EXECVE
            process = subprocess.Popen(
            ["ausearch", "-m", "EXECVE", "--format", "raw"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)
            for line in process.stdout:
                if "sshd" in line:
                    print(line.strip())


        inactivity_timer_stop_event = threading.Event()
        inactivity_timer_reset_event = threading.Event()
        thread_inactivity = threading.Thread(target=inactivity_timer, args=(inactivity_timer_stop_event, inactivity_timer_reset_event))

        def start():
            threads.inactivity_timer.thread_inactivity.start()

        def reset():
            threads.inactivity_timer.inactivity_timer_reset_event.set()

        def stop():
            threads.inactivity_timer.inactivity_timer_stop_event.set()
            threads.inactivity_timer.thread_inactivity.join()


    class listener: #a faire
        
        def listener(listener_stop_event):
            global isAdopted
            
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.bind(('', PORT))
            s.setblocking(0)  # Mettre la socket en mode non bloquant

            while not listener_stop_event.is_set():
                ready = select.select([s], [], [], RECV_TIMEOUT)
                if ready[0]:
                    try:
                        data, addr = s.recvfrom(1024)  # Buffer de 1024 octets
                        message = data.decode('utf-8')
                        
                        if message.startswith("ADPT") and not isAdopted:

                            QUEEN_IP = addr[0]
                            busyfile.modify("queen_IP", QUEEN_IP)
                            isAdopted = True
                            s.sendto("OK".encode('utf-8'), (QUEEN_IP, PORT))
                        
                        elif message.startswith("STAT"):
                            if isAdopted:
                                s.sendto("BUSY".encode('utf-8'), (addr[0], PORT))
                            else:
                                s.sendto("FREE".encode('utf-8'), (addr[0], PORT))

                    except Exception as e:
                        print(f"Erreur lors de la réception: {e}")
                else:
                    if RECV_TIMEOUT > 0:
                        listener_stop_event.set()  # Timeout écoulé, arrêter le listener
            s.close()


        listener_stop_event = threading.Event()
        thread_listener = threading.Thread(target=listener, args=(listener_stop_event,))

        def start():
            threads.listener.thread_listener.start()

        def stop():
            threads.listener.listener_stop_event.set()
            threads.listener.thread_listener.join()






class divers:

    def is_too_old(old_threshold_hours=3):
        global json_data
        format_str = "%d/%m/%Y-%H:%M:%S"
        try:
            date1 = datetime.strptime(json_data['last_updated'], format_str)
            date2 = datetime.strptime(str(time.strftime('%d/%m/%Y-%H:%M:%S')), format_str)
            diff = date2 - date1
            #print("En heures :", diff.total_seconds() / 3600)
            if (diff.total_seconds() / 3600) > old_threshold_hours:
                os.remove(JSON_FILE)
                json_data = {}
        except:
            #print("Problème avec la date")
            busyfile.update_time()
            divers.is_too_old()

    def generateurMDP(IDWorker:str) -> str:
    # Génération de la clé ssh (10 caractères)
    
        graine = int(time.time()/2) #graine (change toutes les 2sec)
    
    #j'ai aucune idée de comment, mais ca fait ce que je veux
        digest = hashlib.blake2s(f"{IDWorker}{graine}".encode()).digest()
        password = base64.urlsafe_b64encode(digest).rstrip(b'=').decode()[:10]
    
        return password