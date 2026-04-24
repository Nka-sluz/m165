import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pymongo import MongoClient, ASCENDING

connection_string = "mongodb://localhost:27017"
client = MongoClient(connection_string)
collection = client["system_monitor"]["power_logs"]


def load_data():
    docs = list(collection.find({}).sort("timestamp", ASCENDING))
    timestamps = [d["timestamp"] for d in docs]
    cpu = [d["cpu"] for d in docs]
    ram_used_gb = [d["ram_used"] / 1024**3 for d in docs]
    ram_total_gb = [d["ram_total"] / 1024**3 for d in docs]
    return timestamps, cpu, ram_used_gb, ram_total_gb


def main():
    timestamps, cpu, ram_used_gb, ram_total_gb = load_data()

    if not timestamps:
        print("No data found in database.")
        return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    fig.suptitle("System Monitor", fontsize=14)

    ax1.plot(timestamps, cpu, color="steelblue", linewidth=0.8)
    ax1.set_ylabel("CPU (%)")
    ax1.set_ylim(0, 100)
    ax1.grid(True, alpha=0.3)

    ax2.plot(timestamps, ram_used_gb, color="tomato", linewidth=0.8, label="Used")
    if ram_total_gb:
        ax2.axhline(y=ram_total_gb[-1], color="gray", linestyle="--", linewidth=0.8, label="Total")
    ax2.set_ylabel("RAM (GB)")
    ax2.set_xlabel("Time")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
