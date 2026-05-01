from pymongo import MongoClient
from room import Room

class Dao_room:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.col = MongoClient(connection_string)["buildings"]["rooms"]

    def create(self, room):
        self.col.insert_one(room.__dict__)

    def read(self, _id):
        room = Room(**self.col.find_one({"_id": _id}))
        return room
    
    def update(self, _id, new_values):
        self.col.update_one({"_id": _id}, {"$set": new_values})

    def delete(self, _id):
        self.col.delete_one({"_id": _id})