import time
import pandas as pd
import joblib
from pathlib import Path

MODEL_PATH = "model.joblib"
CSV_PATH = Path("data/stream.csv")
STATUS_PATH = Path("data/status.txt")

if not Path(MODEL_PATH).exists():
    raise SystemExit("model.joblib not found — run trainer.py after collecting some data from simulator.")

model = joblib.load(MODEL_PATH)
print("Loaded model. Classifier running. Ctrl+C to stop.")

try:
    while True:
        if not CSV_PATH.exists():
            print("Waiting for data...")
            time.sleep(1)
            continue
        df = pd.read_csv(CSV_PATH)
        last = df.tail(1)
        X = last[["motion","sound","temp"]]
        pred = model.predict(X)[0]
        prob = None
        if hasattr(model, "predict_proba"):
            prob = model.predict_proba(X).max()
        out = f"{pred}"
        if prob is not None:
            out += f" ({prob:.2f})"
        print("Prediction:", out)
        STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(STATUS_PATH, "w") as f:
            f.write(pred)
        time.sleep(1)
except KeyboardInterrupt:
    print("Classifier stopped.")
