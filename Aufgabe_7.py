# Aufgabe 7 - GridFS / Files

# Frage: Wie wird die Verbindung der einzelnen Documents zueinander hergestellt?
# GridFS speichert Dateien in zwei Collections: "fs.files" (Metadaten wie Dateiname,
# Grösse, Upload-Datum) und "fs.chunks" (die eigentlichen Rohdaten, aufgeteilt in
# Chunks von je 255 KB). Jeder Eintrag in "fs.chunks" besitzt ein Feld "files_id",
# das auf die "_id" des zugehörigen Dokuments in "fs.files" verweist (Referenz).
# Zusätzlich gibt das Feld "n" die Reihenfolge der Chunks innerhalb der Datei an,
# sodass die Datei beim Lesen in der richtigen Reihenfolge zusammengesetzt wird

# Frage: In welcher Codierung werden die Rohdaten des Files gespeichert?
# Die Rohdaten werden als BSON Binary (BinData, Subtype 0) gespeichert.
# In Tools wie MongoDB Compass erscheinen sie als Base64-kodierte Zeichenketten,
# intern legt MongoDB sie jedoch als binäre Bytes im BSON-Format ab

from pymongo import MongoClient
import gridfs
import os

client = MongoClient('mongodb://localhost:27017/')
db = client['files']
fs = gridfs.GridFS(db)

def save_and_restore_example():
    path = input("File: ").strip()

    with open(path, 'rb') as f:
        file_id = fs.put(f, filename=os.path.basename(path))
    print("File saved")

    grid_out = fs.get(file_id)
    restore_path = os.path.join(".", grid_out.filename)
    with open(restore_path, 'wb') as f:
        f.write(grid_out.read())
    print("File restored")


def add_photo(image_path, album_name):
    """Fügt ein Foto einem Album hinzu. Metadatum 'album' wird via GridFS gespeichert"""
    filename = os.path.basename(image_path)
    with open(image_path, 'rb') as f:
        file_id = fs.put(f, filename=filename, album=album_name)
    print(f"Foto '{filename}' wurde Album '{album_name}' hinzugefügt (id: {file_id})")
    return file_id


def download_album(album_name, output_dir="."):
    """Lädt alle Fotos eines Albums in einen lokalen Ordner herunter"""
    os.makedirs(output_dir, exist_ok=True)
    files = list(fs.find({"album": album_name}))
    if not files:
        print(f"Keine Fotos im Album '{album_name}' gefunden")
        return
    for grid_out in files:
        out_path = os.path.join(output_dir, grid_out.filename)
        with open(out_path, 'wb') as f:
            f.write(grid_out.read())
        print(f"Heruntergeladen: {out_path}")
    print(f"{len(files)} Foto(s) aus Album '{album_name}' heruntergeladen")


def main():
    print("=== Fotoalbum ===")
    print("0 - Beispiel: File speichern und wiederherstellen")
    print("1 - Foto hinzufügen")
    print("2 - Album herunterladen")
    choice = input("Auswahl: ").strip()

    if choice == "0":
        save_and_restore_example()
        return
    if choice == "1":
        image_path = input("Bildpfad: ").strip()
        album_name = input("Albumname: ").strip()
        add_photo(image_path, album_name)
    elif choice == "2":
        album_name = input("Albumname: ").strip()
        output_dir = input("Zielordner (leer = aktuelles Verzeichnis): ").strip() or "."
        download_album(album_name, output_dir)
    else:
        print("Ungültige Auswahl")


if __name__ == "__main__":
    main()
