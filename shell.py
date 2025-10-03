# Installer paramiko si besoin : pip install paramiko
import paramiko
import time

hostname = "adresse_ip_ou_nom"
username = "utilisateur"
password = "motdepasse"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname, username=username, password=password)

# Ouvre un shell interactif
channel = client.invoke_shell()

# Envoie une commande
channel.send('ls -l\n')
time.sleep(1)  # Attendre la réponse

# Lit la sortie
output = channel.recv(4096).decode('utf-8')
print(output)

# Fermer la connexion
channel.close()
client.close()