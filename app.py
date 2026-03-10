import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- CSS TOTAL FIX: CENTER & SMART BUTTONS ---
st.markdown("""
    <style>
    .centered { text-align: center; width: 100%; }
    .clock-style { font-size: 60px; color: #3498db; font-weight: bold; margin-top: -10px; }
    
    /* Center Date Input & Cek Absen Button */
    div[data-testid="stDateInput"] { margin: 0 auto; width: 80% !important; }
    div.stButton > button:first-child {
        background-color: #d35400 !important;
        color: white !important;
        width: 80% !important;
        height: 60px !important;
        font-size: 22px !important;
        font-weight: bold !important;
        margin: 0 auto !important;
        display: block !important;
        border-radius: 15px !important;
    }

    /* Tabel Murni (Lock Columns) */
    .custom-table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 11px; }
    .custom-table th, .custom-table td { padding: 6px 2px; border-bottom: 1px solid #444; text-align: center; }
    .custom-table th { background-color: #222; color: white; }
    .custom-table td.nama-cell { text-align: left; padding-left: 5px; }
    .custom-table tr:nth-child(even) { background-color: rgba(255,255,255,0.05); }

    /* Smart Button Styles */
    .stButton > button.on-btn { background-color: #2980b9 !important; color: white !important; font-size: 10px !important; height: 30px !important; width: 100% !important; border-radius: 5px !important; }
    .stButton > button.off-btn { background-color: #444 !important; color: #888 !important; font-size: 10px !important; height: 30px !important; width: 100% !important; border-radius: 5px !important; cursor: not-allowed !important; }
    .stButton > button.sore-on { background-color: #e67e22 !important; color: white !important; font-size: 10px !important; height: 30px !important; width: 100% !important; border-radius: 5px !important; }
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

# --- JAM WITA ---
now_wita = datetime.now() + timedelta(hours=8)
current_hour = now_wita.hour

st.markdown("<h3 class='centered'>📊 MONITORING ABSENSI KPU HSS</h3>", unsafe_allow_html=True)
st.markdown(f"<div class='centered clock-style'>{now_wita.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

# --- CONTROLS CENTERED ---
tgl_pilihan = st.date_input("Tanggal", now_wita.date(), label_visibility="collapsed")
if st.button("🔍 CEK ABSEN"): st.rerun()

def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        df.columns = df.columns.str.strip()
        for col in df.columns[:2]: df[col] = pd.to_datetime(df[col], dayfirst=True, errors='ignore')
        return df
    except: return pd.DataFrame()

def render_smart_view(df, master, form_url):
    t_pagi, t_sore = datetime.strptime("11:00", "%H:%M").time(), datetime.strptime("16:00", "%H:%M").time()
    log = {}
    if not df.empty:
        df_clean = df.copy()
        time_col, name_col = df_clean.columns[0], df_clean.columns[1]
        df_clean[time_col] = pd.to_datetime(df_clean[time_col], errors='coerce')
        df_day = df_clean[df_clean[time_col].dt.date == tgl_pilihan]
        for _, r in df_day.iterrows():
            nama, jam = str(r[name_col]).strip(), r[time_col].time()
            if nama not in log: log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HDR" if jam <= datetime.strptime("09:00", "%H:%M").time() else "TLT"}
            elif jam >= t_sore: log[nama]["p"] = jam.strftime("%H:%M")

    # TABLE HEADER
    html = """<table class='custom-table'>
    <tr><th style='width:8%'>#</th><th style='width:42%'>NAMA</th><th style='width:18%'>PAGI</th><th style='width:18%'>SORE</th><th style='width:14%'>ST</th></tr>"""
    
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--", "p": "--", "k": "ALPA"})
        clr = "#2ecc71" if d["k"]=="HDR" else "#e67e22" if d["k"]=="TLT" else "#e74c3c"
        html += f"<tr><td>{i}</td><td class='nama-cell'><b>{p}</b></td><td>{d['m']}</td><td>{d['p']}</td><td style='color:{clr}; font-weight:bold;'>{d['k']}</td></tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

    # SMART ABSEN BUTTONS (Beside names in columns)
    st.markdown("<br><p class='centered'><b>TOMBOL ABSEN CEPAT:</b></p>", unsafe_allow_html=True)
    for i, p in enumerate(sorted(master)):
        c_nama, c_pagi, c_sore = st.columns([2, 1, 1])
        c_nama.write(f"**{i+1}. {p.split(',')[0]}**")
        
        # Logika Nyala/Mati Tombol
        is_pagi = current_hour < 11
        
        with c_pagi:
            if st.button("PAGI", key=f"p_{i}", help="Absen Pagi", 
                         type="primary" if is_pagi else "secondary", 
                         disabled=not is_pagi):
                requests.post(form_url, data={"entry.960346359": p})
                st.toast(f"✅ Pagi: {p} Sukses!"); time.sleep(0.5); st.rerun()
        
        with c_sore:
            if st.button("SORE", key=f"s_{i}", 
                         type="primary" if not is_pagi else "secondary", 
                         disabled=is_pagi):
                requests.post(form_url, data={"entry.960346359": p})
                st.toast(f"✅ Sore: {p} Sukses!"); time.sleep(0.5); st.rerun()

tab1, tab2 = st.tabs(["PNS", "PPPK"])
with tab1: render_smart_view(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS)
with tab2: render_smart_view(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK)
