# classifier_firebase.py
import os, time, json
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
import joblib

load_dotenv()

USE_FIREBASE = os.getenv("USE_FIREBASE","0") == "1"
SITES = os.getenv("SITES","site1").split(",")
WINDOW_SIZE = int(os.getenv("WINDOW_SIZE","5"))
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL","1.0"))

MODEL_PATH = Path("model.joblib")
if not MODEL_PATH.exists():
    raise RuntimeError("model.joblib not found. Run trainer.py first.")

saved = joblib.load(MODEL_PATH)
model = saved["model"] if isinstance(saved, dict) and "model" in saved else saved

if USE_FIREBASE:
    import firebase_admin
    from firebase_admin import credentials, db
    cred_path = os.getenv("FIREBASE_CRED_JSON")
    url = os.getenv("FIREBASE_DB_URL")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {"databaseURL": url})
    root_ref = db.reference("/sites")

else:
    print("Running in local CSV mode.")


def fetch_last_n(site_id, n):
    if USE_FIREBASE:
        raw = root_ref.child(site_id).child("raw").order_by_key().limit_to_last(n).get() or {}
        rows = [raw[k] for k in sorted(raw.keys())]
        return rows
    else:
        import pandas as pd
        path = Path("data") / f"{site_id}_stream.csv"
        if not path.exists(): return []
        df = pd.read_csv(path).sort_values("ts")
        return df.tail(n).to_dict("records")


def extract_features(window):
    # Quick compatibility: use the last row's raw sensors (motion, sound, temp)
    # window is a list of dicts (length WINDOW_SIZE). We'll take the latest reading.
    last = window[-1]
    feats = [ last["motion"], last["sound"], last["temp"] ]
    import numpy as np
    return np.array(feats).reshape(1,-1)


def write_status(site_id, status):
    if USE_FIREBASE:
        root_ref.child(site_id).child("status").set(status)
    else:
        path = Path("data") / f"{site_id}_status.json"
        json.dump(status, open(path,"w"))


def main_loop():
    print("Classifier started… polling:", SITES)
    while True:
        for site in SITES:
            rows = fetch_last_n(site.strip(), WINDOW_SIZE)
            if len(rows) < WINDOW_SIZE:
                continue

            x = extract_features(rows)
            pred = model.predict(x)[0]
            prob = None
            if hasattr(model, "predict_proba"):
                prob = float(model.predict_proba(x).max())

            status = {"ts": int(time.time()), "prediction": pred, "prob": prob}
            write_status(site, status)
            print(f"[{site}] → {status}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main_loop()
