import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- MASUKKAN URL WEB APP DARI APPS SCRIPT DI SINI ---
API_PNS = "URL_WEB_APP_PNS_ABANG" 
API_PPPK = "URL_WEB_APP_PPPK_ABANG"

# --- DATA MASTER ---
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

URL_CSV_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_CSV_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

# --- CSS: RESPONSIVE HP ---
st.markdown("""
    <style>
    .centered { text-align: center; width: 100%; }
    .clock-style { font-size: calc(25px + 3vw); color: #3498db; font-weight: bold; margin-bottom: 5px; }
    div[data-testid="stDateInput"] { margin: 0 auto; width: 80% !important; }
    div.stButton > button:first-child {
        background-color: #d35400 !important; color: white !important;
        width: 80% !important; height: 50px !important; margin: 5px auto !important; display: block !important;
    }
    .stHorizontalBlock {
        display: flex !important; flex-wrap: nowrap !important; overflow-x: auto;
        align-items: center !important; border-bottom: 1px solid #444; padding: 8px 0;
    }
    .stButton button[kind="primary"], .stButton button[kind="secondary"] {
        border-radius: 8px !important; width: 45px !important; height: 45px !important; font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

wita_now = datetime.now() + timedelta(hours=8)
st.markdown("<h3 class='centered'>📊 MONITORING ABSENSI KPU HSS</h3>", unsafe_allow_html=True)
st.markdown(f"<div class='centered clock-style'>{wita_now.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

tgl_pilihan = st.date_input("Tanggal", wita_now.date(), label_visibility="collapsed")
if st.button("🔍 CEK DATA TERBARU"): st.rerun()

def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        return pd.read_csv(StringIO(res.text)).dropna(subset=[pd.read_csv(StringIO(res.text)).columns[0]])
    except: return pd.DataFrame()

def kirim_langsung(api_url, nama):
    try:
        requests.get(f"{api_url}?nama={nama}", timeout=10)
        st.toast(f"✅ Berhasil: {nama.split(',')[0]}")
        time.sleep(1)
        st.rerun()
    except: st.error("Gagal koneksi ke server!")

def render_list(df, master, api_url, prefix):
    t_batas, t_pulang = datetime.strptime("09:00", "%H:%M").time(), datetime.strptime("16:00", "%H:%M").time()
    log = {}
    if not df.empty:
        t_str, t_str_alt = tgl_pilihan.strftime('%d/%m/%Y'), tgl_pilihan.strftime('%Y-%m-%d')
        for _, r in df.iterrows():
            ts = str(r.iloc[0])
            if t_str in ts or t_str_alt in ts:
                try:
                    dt = pd.to_datetime(ts)
                    nama, jam = str(r.iloc[1]).strip(), dt.time()
                    if nama not in log:
                        log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HDR" if jam <= t_batas else "TLT"}
                    elif jam >= t_pulang: log[nama]["p"] = jam.strftime("%H:%M")
                except: continue

    st.write("---")
    h1, h2, h3, h4, h5, h6, h7 = st.columns([0.5, 3.5, 1.2, 1.2, 0.8, 1, 1])
    h1.write("#"); h2.write("NAMA"); h3.write("IN"); h4.write("OUT"); h5.write("ST"); h6.write("P"); h7.write("S")
    
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--", "p": "--", "k": "ALPA"})
        clr = "green" if d["k"]=="HDR" else "orange" if d["k"]=="TLT" else "red"
        c1, c2, c3, c4, c5, c6, c7 = st.columns([0.5, 3.5, 1.2, 1.2, 0.8, 1, 1])
        c1.write(i); c2.write(f"**{p.split(',')[0]}**")
        c3.write(d["m"]); c4.write(d["p"]); c5.markdown(f":{clr}[**{d['k']}**]")
        with c6:
            if st.button("P", key=f"p_{prefix}_{i}"): kirim_langsung(api_url, p)
        with c7:
            if st.button("S", key=f"s_{prefix}_{i}"): kirim_langsung(api_url, p)

tab1, tab2 = st.tabs(["👥 PNS", "👥 PPPK"])
with tab1: render_list(fetch_data(URL_CSV_PNS), MASTER_DATA["PNS"], API_PNS, "pns")
with tab2: render_list(fetch_data(URL_CSV_PPPK), MASTER_DATA["PPPK"], API_PPPK, "pppk")
