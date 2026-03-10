import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- CSS: CENTER, BIG, & TABLE BUTTONS ---
st.markdown("""
    <style>
    .centered { text-align: center; width: 100%; }
    .clock-style { font-size: 65px; color: #3498db; font-weight: bold; margin-bottom: 0px; }
    
    /* Center & Big Controls */
    div[data-testid="stDateInput"] { margin: 0 auto; width: 90% !important; }
    div.stButton > button:first-child {
        background-color: #d35400 !important;
        color: white !important;
        width: 90% !important;
        height: 70px !important;
        font-size: 26px !important;
        font-weight: bold !important;
        margin: 20px auto !important;
        display: block !important;
        border-radius: 15px !important;
    }

    /* Tabel HTML Custom: Layout Fix */
    .custom-table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 11px; }
    .custom-table th, .custom-table td { padding: 5px 2px; border-bottom: 1px solid #444; text-align: center; vertical-align: middle; }
    .custom-table th { background-color: #222; color: white; }
    .custom-table td.nama-cell { text-align: left; padding-left: 5px; font-weight: bold; }
    .custom-table tr:nth-child(even) { background-color: rgba(255,255,255,0.05); }

    /* Tombol Dalam Tabel */
    .stButton > button.table-btn {
        padding: 0px !important;
        height: 28px !important;
        font-size: 10px !important;
        width: 100% !important;
        border-radius: 4px !important;
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

# --- TIME LOGIC ---
now_wita = datetime.now() + timedelta(hours=8)
current_hour = now_wita.hour
is_pagi_time = current_hour < 11

st.markdown("<h3 class='centered'>📊 MONITORING ABSENSI KPU HSS</h3>", unsafe_allow_html=True)
st.markdown(f"<div class='centered clock-style'>{now_wita.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

# --- TOP CONTROLS ---
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

def render_table_view(df, master, form_url, prefix):
    t_limit = datetime.strptime("09:00", "%H:%M").time()
    t_sore = datetime.strptime("16:00", "%H:%M").time()
    log = {}
    
    if not df.empty:
        df_clean = df.copy()
        time_col, name_col = df_clean.columns[0], df_clean.columns[1]
        df_clean[time_col] = pd.to_datetime(df_clean[time_col], errors='coerce')
        df_day = df_clean[df_clean[time_col].dt.date == tgl_pilihan]
        for _, r in df_day.iterrows():
            nama, jam = str(r[name_col]).strip(), r[time_col].time()
            if nama not in log: log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HDR" if jam <= t_limit else "TLT"}
            elif jam >= t_sore: log[nama]["p"] = jam.strftime("%H:%M")

    # HEADER TABEL: 7 KOLOM (No, Nama, Pagi, Sore, ST, AbsPagi, AbsSore)
    st.markdown("""<table class='custom-table'>
    <tr><th style='width:6%'>#</th><th style='width:34%'>NAMA</th><th style='width:12%'>PAGI</th><th style='width:12%'>SORE</th>
    <th style='width:10%'>ST</th><th style='width:13%'>ABS.P</th><th style='width:13%'>ABS.S</th></tr>""", unsafe_allow_html=True)
    
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--", "p": "--", "k": "ALPA"})
        clr = "#2ecc71" if d["k"]=="HDR" else "#e67e22" if d["k"]=="TLT" else "#e74c3c"
        
        # Mulai Baris
        st.markdown(f"""<tr style='background-color: {"rgba(255,255,255,0.05)" if i%2==0 else "transparent"}'>
            <td>{i}</td><td class='nama-cell'>{p.split(',')[0]}</td><td>{d['m']}</td><td>{d['p']}</td>
            <td style='color:{clr}; font-weight:bold;'>{d['k']}</td>
            <td id='pagi_{prefix}_{i}'></td><td id='sore_{prefix}_{i}'></td>
        </tr>""", unsafe_allow_html=True)
        
        # Tombol di Samping (Menggunakan columns di dalam loop untuk fungsionalitas)
        col_gap, col_p, col_s = st.columns([7.4, 1.3, 1.3])
        with col_p:
            if st.button("PAGI", key=f"p_{prefix}_{i}", disabled=not is_pagi_time, type="primary" if is_pagi_time else "secondary"):
                requests.post(form_url, data={"entry.960346359": p})
                st.toast(f"✅ Pagi: {p}"); time.sleep(0.5); st.rerun()
        with col_s:
            if st.button("SORE", key=f"s_{prefix}_{i}", disabled=is_pagi_time, type="primary" if not is_pagi_time else "secondary"):
                requests.post(form_url, data={"entry.960346359": p})
                st.toast(f"✅ Sore: {p}"); time.sleep(0.5); st.rerun()
    st.markdown("</table>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
with tab1: render_table_view(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS, "pns")
with tab2: render_table_view(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK, "pppk")
