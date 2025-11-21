# dashboard_multi.py
import streamlit as st
import pandas as pd
import time, json
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
USE_FIREBASE = os.getenv("USE_FIREBASE","0") == "1"
SITES = os.getenv("SITES","site1").split(",")

if USE_FIREBASE:
    import firebase_admin
    from firebase_admin import credentials, db
    cred_path = os.getenv("FIREBASE_CRED_JSON")
    url = os.getenv("FIREBASE_DB_URL")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {"databaseURL": url})
    root_ref = db.reference("/sites")

st.set_page_config(page_title="Crowd Panic — Multi-site", layout="wide")
st.title("Crowd Panic Detection — Multi-site Dashboard")

left, right = st.columns([3,1])

with right:
    site = st.selectbox("Select Site", [s.strip() for s in SITES])
    refresh = st.slider("Refresh (seconds)", 1, 5, 1)
    st.write("Sites available:", ", ".join(SITES))


def fetch_recent_firebase(site, seconds=120):
    raw = root_ref.child(site).child("raw").order_by_key().limit_to_last(300).get() or {}
    rows = [raw[k] for k in sorted(raw.keys())]
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["ts"] = df["ts"].astype(int)
    cutoff = int(time.time()*1000) - seconds*1000
    df = df[df["ts"] >= cutoff]
    df["ts"] = (df["ts"]//1000).astype(int)
    return df


def fetch_status(site):
    if USE_FIREBASE:
        return root_ref.child(site).child("status").get() or {}
    else:
        path = Path("data") / f"{site}_status.json"
        if path.exists():
            return json.load(open(path))
        return {}


with left:
    st.header("Live Data")
    chart_area = st.empty()
    st.markdown("---")
    st.header("Status")
    status_area = st.empty()

while True:
    if USE_FIREBASE:
        df = fetch_recent_firebase(site.strip(), 120)
    else:
        path = Path("data")/f"{site.strip()}_stream.csv"
        if path.exists():
            df = pd.read_csv(path).sort_values("ts")
        else:
            df = pd.DataFrame()

    if df is None or df.empty:
        chart_area.write("No data yet.")
    else:
        df2 = df.copy()
        df2["dt"] = pd.to_datetime(df2["ts"], unit="s")
        df2 = df2.set_index("dt")
        chart_area.line_chart(df2[["motion","sound","temp"]])

    status = fetch_status(site.strip())
    pred = status.get("prediction", None)

    if pred == "panic":
        status_area.markdown("<h2 style='color:red'>STATUS: PANIC 🚨</h2>", unsafe_allow_html=True)
    elif pred == "dense":
        status_area.markdown("<h2 style='color:orange'>STATUS: DENSE</h2>", unsafe_allow_html=True)
    elif pred == "normal":
        status_area.markdown("<h2 style='color:green'>STATUS: NORMAL</h2>", unsafe_allow_html=True)
    else:
        status_area.markdown("<h2>STATUS: -</h2>", unsafe_allow_html=True)

    time.sleep(refresh)
    st.rerun()

