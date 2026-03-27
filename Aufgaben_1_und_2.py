from pymongo import MongoClient
import msvcrt
import subprocess

# Ein ODM (Object Document Mapper) ist das MongoDB-Äquivalent zu einem ORM 
# (Object Relational Mapper) bei relationalen Datenbanken. 
# Er bildet eine Abstraktionsschicht zwischen Python-Objekten und MongoDB-Dokumenten.

connection_string = "mongodb://localhost:27017"
client = MongoClient(connection_string)

def clear():
    subprocess.run("cls", shell=True)

def press_any_key():
    print("\nPress any button to return")
    msvcrt.getch()

def select_database():
    while True:
        clear()
        dbs = client.list_database_names()

        print("Databases")
        if not dbs:
            print("\nNo Database")
            press_any_key()
            return

        for db in dbs:
            print(f" - {db}")

        db_name = input("\nSelect Database: ")

        if db_name in dbs:
            return db_name
        else:
            print(f"\n'{db_name}' not found. Please try again.")
            msvcrt.getch()

def select_collection(db_name):
    while True:
        clear()
        db = client[db_name]
        collections = db.list_collection_names()

        print(f"{db_name}\n")
        print("Collections")

        if not collections:
            print("\nNo Collection")
            press_any_key()
            return None, None

        for col in collections:
            print(f" - {col}")

        col_name = input("\nSelect Collection: ")

        if col_name in collections:
            return db, col_name
        else:
            print(f"\n'{col_name}' not found. Please try again.")
            msvcrt.getch()

def select_document(db_name, db, col_name):
    while True:
        clear()
        collection = db[col_name]
        documents = list(collection.find())

        print(f"{db_name}.{col_name}\n")
        print("Documents")

        if not documents:
            print("\nNo Document")
            press_any_key()
            return None

        id_map = {}
        for doc in documents:
            short_id = str(doc["_id"])
            id_map[short_id] = doc
            print(f" - {short_id}")

        doc_id = input("\nSelect Document: ")

        if doc_id in id_map:
            return id_map[doc_id]
        else:
            print(f"\n'{doc_id}' not found. Please try again.")
            msvcrt.getch()

def show_document(db_name, col_name, document):
    clear()
    doc_id = str(document["_id"])
    print(f"{db_name}.{col_name}.{doc_id}\n")
    for key, value in document.items():
        print(f"{key}: {value}")
    press_any_key()

def main():
    while True:
        db_name = select_database()
        if db_name is None:
            continue

        db, col_name = select_collection(db_name)
        if col_name is None:
            continue

        document = select_document(db_name, db, col_name)
        if document is None:
            continue

        show_document(db_name, col_name, document)

if __name__ == "__main__":
    main()