from room import Room
from dao_room import Dao_room

dao_room = Dao_room("mongodb://localhost:27017/")

# Create
room_create = Room("Pilatus", 12, True)
dao_room.create(room_create)

# Read
room_read = dao_room.read(room_create._id)
print(f"Name: {room_read.name}, Seats: {room_read.seats}, Reservable: {room_read.is_reservable}")

# Update
dao_room.update(room_read._id, {"name": "Rigi", "seats": 8, "is_reservable": False})
room_read = dao_room.read(room_read._id)
print(f"Name: {room_read.name}, Seats: {room_read.seats}, Reservable: {room_read.is_reservable}")

# Delete
dao_room.delete(room_read._id)
print(f"Deleted room: {room_read.name}")