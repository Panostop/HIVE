from libserver import *
import threading
from prettytable import PrettyTable 
import socket
import random
from colorama import Fore, Back, Style
import paramiko
from pathlib import Path

workers_list = []
workers_states = []

variables_names = []
variables_types = []
variables_values = []

KEY = Path("ssh_pubkeyfile")

command = ""

homepage = """

                                       #@@@@                                    
                                    %@@@# *@@@@:                                
                                .@@@@@       %@@@@=                             
                             :@@@@#     ...     +@@@@+                          
                            @@@-     .........     :@@@                         
                            @@+   ................  .@@                         
                    @@@@@@@@@@* ....................-@@@@@@@@@@                 
                 %@@@#   .#@@@@:....................%@@@%.   +@@@@.             
             -@@@@#      ...@@@@@@+.............=%@@@@@...      +@@@@#          
          =@@@@#      ......%@  #@@@@#.......:#@@@#  @@......      =@@@@#       
          #@@     ..........@@     @@*.......*@@     @@:........      #@@       
          #@@   ............@@     @@+.......+@@     @@:...........   *@@       
          #@@   ............#%@@#  @@+.......*@@   @@@#............   *@@       
          #@@   ..............:#@@@@@*...... *@@@@@#-..............   *@@       
          #@@   ..................#@@@@+. .:%@@@%-.................   *@@       
          #@@   ...................@@@@@@@@@@@@@...................   *@@       
          #@@   ...................@@*       -@@...................   *@@       
          #@@+     ...............#@@+       +@@#................    -@@@       
           =@@@@%     .........%@@@@:          @@@@#..........     @@@@         
             =@@@@@@     ...@@@@@@+              @@@@@@-...    #@@@@@           
                  #@@@@   @@@#                        @@@@   @@@@       
                     #@@@@#                             #@@@@#
            
             _   _ _____ _   _ _____                                         
            | | | |_   _| | | |  ___|                                        
            | |_| | | | | | | | |__    ______   ___  ___ _ ____   _____ _ __ 
            |  _  | | | | | | |  __|  |______| / __|/ _ \ '__\ \ / / _ \ '__|
            | | | |_| |_\ \_/ / |___           \__ \  __/ |   \ V /  __/ |   
            \_| |_/\___/ \___/\____/           |___/\___|_|    \_/ \___|_|                                                                   
             ______ _____ _____ ___       _   _               _                  
             | ___ \  ___|_   _/ _ \     | | | |             (_)                 
             | |_/ / |__   | |/ /_\ \    | | | | ___ _ __ ___ _  ___  _ __       
             | ___ \  __|  | ||  _  |    | | | |/ _ \ '__/ __| |/ _ \| '_ \      
             | |_/ / |___  | || | | |    \ \_/ /  __/ |  \__ \ | (_) | | | |      
             \____/\____/  \_/\_| |_/     \___/ \___|_|  |___/_|\___/|_| |_|     
                                                                 
                                                                 


                                                                                
                                        """






def write(style, color, text):
    print(style + color + text + Style.RESET_ALL)





def server():
    global command, workers_list, workers_states
    target = "ALL"
    try:
        #threads.thread_udp_listener.start()
        while command != "exit":
            command = input(f"{target}> ").strip().lower()

            if command == "help":
                print("Commandes disponibles :")
                print("  help       - Afficher cette aide")
                print("  list       - Lister les workers détectés")
                print("  exit       - Quitter le programme")

            elif command == "list":
                if workers_list:
                    create_table(["Worker IP", "State"], len(workers_list), [workers_list, workers_states])
                else:
                    print("Aucun worker détecté.")

            elif command == "add_worker":
                # Configurer la socket UDP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # Autoriser l'envoi broadcast
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                # Lier sur toutes les interfaces pour recevoir les réponses
                s.bind(('', PORT))
                
                if command.split(" ")[1] in workers_list:
                    write(Style.NORMAL, Fore.YELLOW, f"Le worker {command.split(' ')[1]} est déjà dans la liste.")
                else:
                    send_ip = command.split(" ")[1]
                    try:
                        s.sendto("ADPT".encode('utf-8'), (send_ip, PORT))
                        
                    except Exception as e:
                        write(Style.NORMAL, Fore.RED, f"Erreur lors de l'envoi du message au worker {send_ip} : {e}")

            elif command == "exit":
                print("Fermeture du serveur...")
                #threads.thread_udp_listener.stop()
                break

            elif command.startswith("create_var"):
                print("variable personnalisée créée (fonctionnalité non implémentée).")

            elif command.startswith("change_target"):

                target = command.split(" ")[1].upper()
                
                if target != "ALL" and target not in workers_list:
                    print(f"Worker {target} non trouvé. Cible remise à ALL.")
                    target = "ALL"
                else:
                    print(f"cible changée ({target} --> {command.split(" ")[1].upper()})")

                

            else:
                if command:
                    if workers_list:
                        if target != "ALL":
                            if target in workers_list:
                                print(f"Envoi de la commande '{command}' à {target} (fonctionnalité non implémentée).")
                            else:
                                print(f"Worker {target} non trouvé. Commande non envoyée.")

                        else: 
                            for workers in active_workers:
                                print(f"Envoi de la commande '{command}' à {workers} (fonctionnalité non implémentée).")
                    else:
                        print("Aucun worker actif. Commande non envoyée.")
                        

    except Exception as e:
        print(f"Erreur dans la boucle principale du serveur : {e}")








print(Fore.YELLOW + homepage)
print(Fore.WHITE)
print("Bienvenue sur le serveur BrainHive")
server()
write(Style.BRIGHT, Fore.YELLOW, "Fermeture du serveur BrainHive...")
print("Bienvenue sur le serveur BrainHive")