from pymongo import MongoClient
from joke import Joke

class Dao_joke:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.col = MongoClient(connection_string)["literature"]["jokes"]

    def insert(self, joke):
        self.col.insert_one(joke.__dict__)

    def get_category(self, category):
        jokes = list(self.col.find({"category": category}))
        return [Joke(**joke) for joke in jokes]

    def delete(self, _id):
        self.col.delete_one({"_id": _id})