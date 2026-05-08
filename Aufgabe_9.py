from pymongo import MongoClient
import gridfs
import os
import subprocess
import tempfile
import random
from collections import deque

client = MongoClient('mongodb://localhost:27017/')
db = client['jukebox']
fs = gridfs.GridFS(db)
songs_col = db['songs']

playlist = deque()  # FIFO


# ---- Song class ----

class Song:
    def __init__(self, name, artist, album=None, genre=None, year=None, file_id=None, _id=None):
        self.name = name
        self.artist = artist
        self.album = album
        self.genre = genre
        self.year = year
        self.file_id = file_id
        self._id = _id

    def to_dict(self):
        d = {'name': self.name, 'artist': self.artist}
        if self.album is not None:  d['album']   = self.album
        if self.genre is not None:  d['genre']   = self.genre
        if self.year  is not None:  d['year']    = self.year
        if self.file_id is not None: d['file_id'] = self.file_id
        return d

    @staticmethod
    def from_dict(d):
        return Song(
            name=d['name'], artist=d['artist'],
            album=d.get('album'), genre=d.get('genre'),
            year=d.get('year'), file_id=d.get('file_id'),
            _id=d.get('_id'),
        )

    def __str__(self):
        info = f"'{self.name}' von {self.artist}"
        extras = []
        if self.album: extras.append(f"Album: {self.album}")
        if self.genre: extras.append(f"Genre: {self.genre}")
        if self.year:  extras.append(f"Jahr: {self.year}")
        return info + (f" ({', '.join(extras)})" if extras else "")


# ---- Helpers ----

def search_songs(name="", artist="", album="", genre=""):
    """Case-insensitive partial match on all provided fields (AND-combined)."""
    query = {}
    if name:   query['name']   = {'$regex': name,   '$options': 'i'}
    if artist: query['artist'] = {'$regex': artist, '$options': 'i'}
    if album:  query['album']  = {'$regex': album,  '$options': 'i'}
    if genre:  query['genre']  = {'$regex': genre,  '$options': 'i'}
    return [Song.from_dict(d) for d in songs_col.find(query)]


def search_by_term(term):
    """Search name OR artist — used in management pick."""
    return [Song.from_dict(d) for d in songs_col.find({
        '$or': [
            {'name':   {'$regex': term, '$options': 'i'}},
            {'artist': {'$regex': term, '$options': 'i'}},
        ]
    })]


def pick_from_list(songs):
    """Print numbered list and return chosen Song, or None on cancel."""
    if not songs:
        print("Keine Songs gefunden.")
        return None
    for i, s in enumerate(songs, 1):
        print(f"  {i}. {s}")
    while True:
        raw = input("Auswahl (0 = Abbrechen): ").strip()
        if raw == "0":
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(songs):
            return songs[int(raw) - 1]
        print("Ungültige Eingabe.")


def play_song(song):
    """Extract audio from GridFS into a temp file and play via the default Windows media player."""
    if not song.file_id:
        print(f"Kein Audiofile für '{song.name}' hinterlegt.")
        return
    try:
        grid_out = fs.get(song.file_id)
    except Exception:
        print(f"Audiofile für '{song.name}' nicht gefunden.")
        return

    ext = os.path.splitext(grid_out.filename)[1] or '.mp3'
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(grid_out.read())
        tmp_path = tmp.name

    print(f"  Spiele: {song}")
    print("  (Mediaplayer schliessen, um fortzufahren)")
    try:
        # start /wait blocks until the user closes the media player window
        subprocess.run(f'start /wait "" "{tmp_path}"', shell=True)
    finally:
        os.unlink(tmp_path)


# ---- Management ----

def add_song():
    print("\n-- Song hinzufügen --")
    name = input("Name (Pflichtfeld): ").strip()
    artist = input("Interpret (Pflichtfeld): ").strip()
    if not name or not artist:
        print("Name und Interpret sind Pflichtfelder.")
        return

    album  = input("Album (optional): ").strip() or None
    genre  = input("Genre (optional): ").strip() or None
    year_s = input("Erscheinungsjahr (optional): ").strip()
    year   = int(year_s) if year_s.isdigit() else None

    path = input("Pfad zum Audiofile: ").strip()
    if not os.path.isfile(path):
        print("Datei nicht gefunden.")
        return

    with open(path, 'rb') as f:
        file_id = fs.put(f, filename=os.path.basename(path))

    songs_col.insert_one(Song(name, artist, album, genre, year, file_id).to_dict())
    print(f"Song '{name}' gespeichert.")


def edit_song():
    print("\n-- Song ändern --")
    term = input("Suchbegriff (Name oder Interpret): ").strip()
    song = pick_from_list(search_by_term(term))
    if not song:
        return

    print(f"\nAktuell: {song}")
    print("(Leer lassen = unverändert)")
    name   = input(f"Name [{song.name}]: ").strip()           or song.name
    artist = input(f"Interpret [{song.artist}]: ").strip()    or song.artist
    album  = input(f"Album [{song.album or ''}]: ").strip()   or song.album
    genre  = input(f"Genre [{song.genre or ''}]: ").strip()   or song.genre
    year_s = input(f"Jahr [{song.year or ''}]: ").strip()
    year   = int(year_s) if year_s.isdigit() else song.year

    songs_col.update_one(
        {'_id': song._id},
        {'$set': {'name': name, 'artist': artist, 'album': album, 'genre': genre, 'year': year}},
    )
    print("Song aktualisiert.")


def delete_song():
    print("\n-- Song löschen --")
    term = input("Suchbegriff (Name oder Interpret): ").strip()
    song = pick_from_list(search_by_term(term))
    if not song:
        return

    confirm = input(f"'{song.name}' wirklich löschen? (j/n): ").strip().lower()
    if confirm == 'j':
        if song.file_id:
            fs.delete(song.file_id)
        songs_col.delete_one({'_id': song._id})
        print("Song gelöscht.")
    else:
        print("Abgebrochen.")


def management_menu():
    while True:
        print("\n=== Management ===")
        print("1 - Song hinzufügen")
        print("2 - Song ändern")
        print("3 - Song löschen")
        print("0 - Zurück")
        choice = input("Auswahl: ").strip()
        if   choice == "1": add_song()
        elif choice == "2": edit_song()
        elif choice == "3": delete_song()
        elif choice == "0": break
        else: print("Ungültige Auswahl.")


# ---- Player ----

def search_and_add():
    print("\n-- Song suchen --")
    name   = input("Name   (leer = beliebig): ").strip()
    artist = input("Interpret (leer = beliebig): ").strip()
    album  = input("Album  (leer = beliebig): ").strip()
    genre  = input("Genre  (leer = beliebig): ").strip()

    results = search_songs(name=name, artist=artist, album=album, genre=genre)
    song = pick_from_list(results)
    if song:
        playlist.append(song)
        print(f"'{song.name}' zur Playlist hinzugefügt.")


def show_playlist():
    print("\n-- Playlist --")
    if not playlist:
        print("Die Playlist ist leer.")
        return
    for i, s in enumerate(playlist, 1):
        print(f"  {i}. {s}")


def play_playlist():
    print("\n-- Abspielen --")
    if playlist:
        while playlist:
            play_song(playlist.popleft())
    else:
        count = songs_col.count_documents({})
        if count == 0:
            print("Keine Songs in der Datenbank.")
            return
        doc = songs_col.find().skip(random.randint(0, count - 1)).limit(1).next()
        print("Playlist leer – spiele zufälligen Song.")
        play_song(Song.from_dict(doc))


def player_menu():
    while True:
        print("\n=== Player ===")
        print("1 - Song suchen und zur Playlist hinzufügen")
        print("2 - Playlist anzeigen")
        print("3 - Playlist abspielen")
        print("0 - Zurück")
        choice = input("Auswahl: ").strip()
        if   choice == "1": search_and_add()
        elif choice == "2": show_playlist()
        elif choice == "3": play_playlist()
        elif choice == "0": break
        else: print("Ungültige Auswahl.")


# ---- Main ----

def main():
    while True:
        print("\n=== Jukebox ===")
        print("1 - Management")
        print("2 - Player")
        print("0 - Beenden")
        choice = input("Auswahl: ").strip()
        if   choice == "1": management_menu()
        elif choice == "2": player_menu()
        elif choice == "0": break
        else: print("Ungültige Auswahl.")


if __name__ == "__main__":
    main()
