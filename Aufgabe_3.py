
from pymongo import MongoClient
from datetime import datetime


connection_string = "mongodb://localhost:27017"
client = MongoClient(connection_string)
dbRestaurants = client["restaurants"]
collectionRestaurants = dbRestaurants["restaurants"]

def printStadtbezirken():
    stadtbezirken = collectionRestaurants.distinct("borough")
    stadtbezirken.pop(stadtbezirken.index("Missing")) 
    print("Stadtbezirken:")
    for stadtbezirk in stadtbezirken:
        print(f" - {stadtbezirk}")

def printTop3Restaurants():
    pipeline = [
        {"$unwind": "$grades"},
        {"$match": {"grades.score": {"$gt": 0}}},
        {"$group": {
            "_id": "$restaurant_id",
            "name": {"$first": "$name"},
            "borough": {"$first": "$borough"},
            "avgScore": {"$avg": "$grades.score"},
            "gradeCount": {"$sum": 1}
        }},
        {"$match": {"gradeCount": {"$gte": 3}}},
        {"$sort": {"avgScore": 1}},
        {"$limit": 3}
    ]
    top3 = collectionRestaurants.aggregate(pipeline)
    print("\nTop 3 Restaurants (niedrigster Durchschnittsscore):")
    for i, r in enumerate(top3, 1):
        print(f" {i}. {r['name']} ({r['borough']}) - Avg Score: {r['avgScore']:.2f}")


def searchRestaurants():
    name = input("\nName (leer lassen zum Ignorieren): ").strip()
    cuisine = input("Küche (leer lassen zum Ignorieren): ").strip()

    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if cuisine:
        query["cuisine"] = {"$regex": cuisine, "$options": "i"}

    results = list(collectionRestaurants.find(query, {"_id": 1, "name": 1, "cuisine": 1, "borough": 1}))

    if not results:
        print("Keine Restaurants gefunden.")
        return None

    print(f"\n{len(results)} Restaurant(e) gefunden:")
    for i, r in enumerate(results, 1):
        print(f" {i}. {r['name']} | Küche: {r['cuisine']} | Bezirk: {r['borough']}")

    if len(results) == 1:
        selected = results[0]
    else:
        while True:
            choice = input("\nRestaurant auswählen (Nummer): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(results):
                selected = results[int(choice) - 1]
                break
            print(f"Bitte eine Zahl zwischen 1 und {len(results)} eingeben.")

    print(f"\nAusgewählt: {selected['name']}")
    return selected["_id"]

def addBewertung(restaurant_id):
    grade = input("Note (A / B / C): ").strip().upper()
    while grade not in ("A", "B", "C"):
        grade = input("Ungültige Note. Bitte A, B oder C eingeben: ").strip().upper()

    while True:
        score = input("Score (ganze Zahl >= 0): ").strip()
        if score.isdigit():
            score = int(score)
            break
        print("Bitte eine gültige ganze Zahl eingeben.")

    new_grade = {
        "date": datetime.now(),
        "grade": grade,
        "score": score
    }

    collectionRestaurants.update_one(
        {"_id": restaurant_id},
        {"$push": {"grades": new_grade}}
    )
    print("Bewertung erfolgreich hinzugefügt.")

def main():
    printStadtbezirken()
    printTop3Restaurants()
    restaurant_id = searchRestaurants()
    if restaurant_id is not None:
        addBewertung(restaurant_id)

if __name__ == "__main__":
    main()