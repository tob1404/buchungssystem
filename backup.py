import shutil
from datetime import datetime
import os
import time

# Render: /backup (Persistent Disk)
# Lokal: ./backup (relativer Ordner)
if os.path.exists("/backup"):
    BACKUP_DIR = "/backup"
else:
    BACKUP_DIR = "backup"

FILES_TO_BACKUP = {
    "data/buchungen.csv": "buchungen",
    "data/ticketgenerator.csv": "ticketgenerator"
}

def run_backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    
    for src_path, name in FILES_TO_BACKUP.items():
        if os.path.exists(src_path):
            dest_filename = f"{name}_{timestamp}.csv"
            dest_path = os.path.join(BACKUP_DIR, dest_filename)
            shutil.copy2(src_path, dest_path)
            print(f"[{timestamp}] Backup erstellt: {dest_path}")
        else:
            print(f"[{timestamp}] Datei nicht gefunden: {src_path}")

if __name__ == "__main__":
    while True:
        run_backup()
        time.sleep(6 * 60 * 60)  # alle 6 Stunden
