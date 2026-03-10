import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- CSS TOTAL FIX: LOCK TABLE ALIGNMENT ---
st.markdown("""
    <style>
    /* Jam & Judul di Tengah */
    .centered { text-align: center; width: 100%; }
    .clock-style { font-size: 50px; color: #3498db; font-weight: bold; margin-top: -10px; }
    
    /* Tombol Cek Absen Orange */
    div.stButton > button:first-child {
        background-color: #d35400 !important;
        color: white !important;
        width: 200px !important;
        margin: 0 auto !important;
        display: block !important;
    }

    /* Tabel Murni (Kunci Biar Gak Melorot) */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed; /* Kunci lebar kolom */
        font-size: 12px;
    }
    .custom-table th, .custom-table td {
        padding: 8px 2px;
        border-bottom: 1px solid #444;
        text-align: center;
        overflow: hidden;
    }
    .custom-table th { background-color: #222; color: white; }
    .custom-table td.nama { text-align: left; overflow: visible; white-space: normal; }
    
    /* Zebra Stripes */
    .custom-table tr:nth-child(even) { background-color: rgba(255,255,255,0.05); }

    /* Tombol Absen di Tabel */
    .btn-row {
        background-color: #2980b9;
        color: white;
        border: none;
        padding: 6px 10px;
        border-radius: 5px;
        font-size: 11px;
        font-weight: bold;
        text-decoration: none;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA MASTER ---
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"

# --- HEADER ---
wita_now = datetime.now() + timedelta(hours=8)
st.markdown("<h3 class='centered'>📊 MONITORING ABSENSI KPU HSS</h3>", unsafe_allow_html=True)
st.markdown(f"<div class='centered clock-style'>{wita_now.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

# --- KONTROL ---
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    tgl_pilihan = st.date_input("Tanggal", wita_now.date(), label_visibility="collapsed")
    if st.button("🔍 CEK ABSEN"): st.rerun()

def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        df.columns = df.columns.str.strip()
        for col in df.columns[:2]:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors='ignore')
        return df
    except: return pd.DataFrame()

def render_view(df, master, form_url):
    t_m, t_p = datetime.strptime("09:00", "%H:%M").time(), datetime.strptime("16:00", "%H:%M").time()
    log = {}
    if not df.empty:
        df_clean = df.copy()
        time_col, name_col = df_clean.columns[0], df_clean.columns[1]
        df_clean[time_col] = pd.to_datetime(df_clean[time_col], errors='coerce')
        df_day = df_clean[df_clean[time_col].dt.date == tgl_pilihan]
        for _, r in df_day.iterrows():
            nama, jam = str(r[name_col]).strip(), r[time_col].time()
            if nama not in log: log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HDR" if jam <= t_m else "TLT"}
            elif jam >= t_p: log[nama]["p"] = jam.strftime("%H:%M")

    # BANGUN TABEL MURNI (CSS LOCK)
    html = """<table class='custom-table'>
    <tr><th style='width:10%'>#</th><th style='width:45%'>NAMA</th><th style='width:15%'>M</th><th style='width:15%'>P</th><th style='width:15%'>ST</th></tr>"""
    
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--", "p": "--", "k": "ALPA"})
        clr = "#2ecc71" if d["k"]=="HDR" else "#e67e22" if d["k"]=="TLT" else "#e74c3c"
        html += f"<tr><td>{i}</td><td class='nama'><b>{p}</b></td><td>{d['m']}</td><td>{d['p']}</td><td style='color:{clr}; font-weight:bold;'>{d['k']}</td></tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)
    
    # Tombol Absen ditaruh di bawah tabel biar lega
    st.markdown("<br><p class='centered'><b>TOMBOL ABSEN CEPAT:</b></p>", unsafe_allow_html=True)
    btns = st.columns(2)
    for i, p in enumerate(sorted(master)):
        with btns[i % 2]:
            if st.button(f"ABSEN: {p.split(',')[0]}", key=f"x_{p}_{i}"):
                requests.post(form_url, data={"entry.960346359": p})
                st.toast(f"✅ {p} OK!"); time.sleep(0.5); st.rerun()

tab1, tab2 = st.tabs(["PNS", "PPPK"])
with tab1: render_view(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS)
with tab2: render_view(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK)
