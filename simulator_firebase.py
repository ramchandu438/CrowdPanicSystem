# simulator_firebase.py
import time, os, random
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
USE_FIREBASE = os.getenv("USE_FIREBASE", "0") == "1"
SITES = os.getenv("SITES", "site1").split(",")
INTERVAL = float(os.getenv("SIM_INTERVAL", "1.0"))

if USE_FIREBASE:
    import firebase_admin
    from firebase_admin import credentials, db
    cred_path = os.getenv("FIREBASE_CRED_JSON")
    url = os.getenv("FIREBASE_DB_URL")
    if not cred_path or not url:
        raise RuntimeError("Set FIREBASE_CRED_JSON and FIREBASE_DB_URL in .env")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {"databaseURL": url})
    root_ref = db.reference("/sites")
else:
    import pandas as pd
    DATA_DIR = Path("data")
    DATA_DIR.mkdir(exist_ok=True)

def sample_normal():
    return {"motion": random.randint(0,5), "sound": round(random.uniform(40,60),1), "temp": round(random.uniform(25,30),1)}

def sample_dense():
    return {"motion": random.randint(6,15), "sound": round(random.uniform(60,80),1), "temp": round(random.uniform(28,33),1)}

def sample_panic():
    return {"motion": random.randint(16,30), "sound": round(random.uniform(85,120),1), "temp": round(random.uniform(30,36),1)}

def pick_scenario(mode="random", tick=0):
    if mode=="demo":
        c = tick % 60
        if c < 30: return sample_normal()
        elif c < 45: return sample_dense()
        else: return sample_panic()

    # random mode
    r = random.random()
    if r < 0.7: return sample_normal()
    elif r < 0.9: return sample_dense()
    else: return sample_panic()

def push_record(site_id, rec):
    ts = int(time.time()*1000)  # ms
    row = {"ts": ts, **rec}
    if USE_FIREBASE:
        ref = root_ref.child(site_id).child("raw").child(str(ts))
        ref.set(row)
    else:
        import pandas as pd
        path = Path("data") / f"{site_id}_stream.csv"
        df = pd.DataFrame([{"ts": ts//1000, **rec}])
        header = not path.exists()
        df.to_csv(path, mode="a", index=False, header=header)

def main():
    print("Simulator started. USE_FIREBASE =", USE_FIREBASE)
    mode = "demo" if os.getenv("SIM_MODE","demo")=="demo" else "random"
    tick = 0
    try:
        while True:
            for site in SITES:
                site = site.strip()
                rec = pick_scenario(mode, tick)
                push_record(site, rec)
                print(f"{datetime.utcnow().isoformat()} -> {site}: {rec}")
            tick += 1
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("Stopped.")

if __name__ == "__main__":
    main()
