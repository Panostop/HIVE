import paramiko
import time
import os

hostname = "adresse_ip_ou_nom"
username = "utilisateur"
password = "motdepasse"  # Mot de passe pour la première connexion
pubkey_path = "chemin/vers/id_rsa.pub"  # Chemin vers la clé publique
privkey_path = "chemin/vers/id_rsa"     # Chemin vers la clé privée

# 1. Lire la clé publique
with open(pubkey_path, "r") as f:
    pubkey = f.read().strip()

# 2. Connexion SSH avec mot de passe
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname, username=username, password=password)

# 3. Ajouter la clé publique dans authorized_keys
cmd = f'mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo "{pubkey}" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
stdin, stdout, stderr = client.exec_command(cmd)
stdout.channel.recv_exit_status()  # Attendre la fin

client.close()

# 4. Connexion SSH avec la clé privée
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname, username=username, key_filename=privkey_path)

channel = client.invoke_shell()
channel.send('ls -l\n')
time.sleep(1)
output = channel.recv(4096).decode('utf-8')
print(output)

channel.close()
client.close()