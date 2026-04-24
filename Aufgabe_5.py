import time
import psutil
from datetime import datetime
from pymongo import MongoClient, ASCENDING

connection_string = "mongodb://localhost:27017"
client = MongoClient(connection_string)
db = client["system_monitor"]
collection = db["power_logs"]

MAX_LOGS = 10000


class Power:
    def __init__(self, cpu=None, ram_total=None, ram_used=None, timestamp=None):
        if cpu is None and ram_total is None and ram_used is None and timestamp is None:
            self.timestamp = datetime.now()
            mem = psutil.virtual_memory()
            self.cpu = psutil.cpu_percent(interval=0.1)
            self.ram_total = mem.total
            self.ram_used = mem.used
        else:
            self.cpu = cpu
            self.ram_total = ram_total
            self.ram_used = ram_used
            self.timestamp = timestamp

    def to_dict(self):
        return {
            "cpu": self.cpu,
            "ram_total": self.ram_total,
            "ram_used": self.ram_used,
            "timestamp": self.timestamp,
        }


def trim_logs():
    count = collection.count_documents({})
    if count > MAX_LOGS:
        oldest = list(
            collection.find({}, {"_id": 1})
            .sort("timestamp", ASCENDING)
            .limit(count - MAX_LOGS)
        )
        ids = [doc["_id"] for doc in oldest]
        collection.delete_many({"_id": {"$in": ids}})


def main():
    print("Logging CPU and RAM every second. Press Ctrl+C to stop.")
    while True:
        power = Power()
        collection.insert_one(power.to_dict())
        trim_logs()
        print(
            f"[{power.timestamp.strftime('%H:%M:%S')}] "
            f"CPU: {power.cpu:.1f}%  "
            f"RAM: {power.ram_used / 1024**3:.2f} GB / {power.ram_total / 1024**3:.2f} GB"
        )
        time.sleep(1)


if __name__ == "__main__":
    main()
