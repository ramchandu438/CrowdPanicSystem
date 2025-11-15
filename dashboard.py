import streamlit as st
import pandas as pd
import time
from pathlib import Path

CSV_PATH = Path("data/stream.csv")
STATUS_PATH = Path("data/status.txt")

st.set_page_config(layout="wide")
st.title("Crowd Panic Detection — Demo (Sensor)")

status_placeholder = st.empty()
chart_placeholder = st.empty()

def read_status():
    if STATUS_PATH.exists():
        return STATUS_PATH.read_text().strip()
    return "unknown"

def read_recent(n=120):
    if not CSV_PATH.exists():
        return None
    df = pd.read_csv(CSV_PATH)
    df = df.sort_values("ts")
    now = int(time.time())
    return df[df["ts"] >= now - n]

while True:
    df = read_recent(120)
    if df is None or df.empty:
        chart_placeholder.write("No data yet. Run simulator.py")
    else:
        df2 = df.copy()
        df2["dt"] = pd.to_datetime(df2["ts"], unit="s")
        df2 = df2.set_index("dt")
        chart_placeholder.line_chart(df2[["motion","sound","temp"]])

    status = read_status()
    if status == "panic":
        status_placeholder.markdown("<h2 style='color:red'>STATUS: PANIC 🚨</h2>", unsafe_allow_html=True)
    elif status == "dense":
        status_placeholder.markdown("<h2 style='color:orange'>STATUS: DENSE</h2>", unsafe_allow_html=True)
    elif status == "normal":
        status_placeholder.markdown("<h2 style='color:green'>STATUS: NORMAL</h2>", unsafe_allow_html=True)
    else:
        status_placeholder.markdown("<h2>STATUS: -</h2>", unsafe_allow_html=True)

    time.sleep(1)
    st.rerun()   # NEW FIXED LINE
