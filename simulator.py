import time
import random
import pandas as pd
from pathlib import Path

CSV_PATH = Path("data/stream.csv")
CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

def generate_record():
    chance = random.random()

    if chance < 0.7:
        return {
            "ts": int(time.time()),
            "motion": random.randint(1,5),
            "sound": random.randint(40,60),
            "temp": random.randint(25,30),
            "label": "normal"
        }
    elif chance < 0.9:
        return {
            "ts": int(time.time()),
            "motion": random.randint(5,15),
            "sound": random.randint(60,80),
            "temp": random.randint(28,35),
            "label": "dense"
        }
    else:
        return {
            "ts": int(time.time()),
            "motion": random.randint(15,30),
            "sound": random.randint(80,120),
            "temp": random.randint(30,40),
            "label": "panic"
        }

def append_row(row):
    df = pd.DataFrame([row])
    header = not CSV_PATH.exists()
    df.to_csv(CSV_PATH, mode="a", index=False, header=header)

if __name__ == "__main__":
    print("Simulator started — generating one record per second. Ctrl+C to stop.")
    try:
        while True:
            rec = generate_record()
            append_row(rec)
            print(rec)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Simulator stopped.")
