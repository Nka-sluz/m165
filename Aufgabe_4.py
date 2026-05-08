import os
from pymongo import MongoClient

# --- Umgebungsvariablen in Python lesen ---
# os.environ      -> Dictionary aller Umgebungsvariablen
# os.environ["KEY"]       -> KeyError wenn nicht vorhanden
# os.environ.get("KEY")   -> None wenn nicht vorhanden (sicherer)
# os.getenv("KEY", "default") -> Fallback-Wert wenn nicht vorhanden

# Exemplarisch: PATH-Umgebungsvariable auslesen und ausgeben
path = os.environ.get("PATH", "PATH nicht gefunden")
print("=== PATH Umgebungsvariable ===")
for entry in path.split(os.pathsep):
    print(f"  {entry}")

# --- Connection-String aus Umgebungsvariable lesen ---
# Umgebungsvariable setzen (Windows CMD):  set MONGO_CONNECTION_STRING=mongodb+srv://...
# Umgebungsvariable setzen (PowerShell):   $env:MONGO_CONNECTION_STRING = "mongodb+srv://..."
# Umgebungsvariable setzen (Linux/macOS):  export MONGO_CONNECTION_STRING="mongodb+srv://..."

connection_string = os.environ.get("MONGO_CONNECTION_STRING")

if not connection_string:
    print("\nFehler: Umgebungsvariable 'MONGO_CONNECTION_STRING' ist nicht gesetzt")
    print("Bitte setzen Sie die Variable z.B. mit:")
    print("  PowerShell: $env:MONGO_CONNECTION_STRING = \"mongodb+srv://user:pass@cluster.mongodb.net/\"")
    exit(1)

print(f"\n=== Verbindung zur Cloud-Datenbank ===")
print(f"Connection-String aus Umgebungsvariable gelesen (Länge: {len(connection_string)} Zeichen)")

client = MongoClient(connection_string)

# Verbindung testen
try:
    client.admin.command("ping")
    print("Verbindung erfolgreich!")
    print("\nVerfügbare Datenbanken:")
    for db_name in client.list_database_names():
        print(f"  - {db_name}")
except Exception as e:
    print(f"Verbindung fehlgeschlagen: {e}")
finally:
    client.close()
