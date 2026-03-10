import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- CSS: BIG BUTTONS, ZEBRA, & FULL MOBILE OPTIMIZATION ---
st.markdown("""
    <style>
    .centered { text-align: center; width: 100%; }
    .clock-style { font-size: 70px; color: #3498db; font-weight: bold; margin-bottom: 5px; }
    
    /* Center & Giant Controls */
    div[data-testid="stDateInput"] { margin: 0 auto; width: 90% !important; }
    div.stButton > button:first-child {
        background-color: #d35400 !important;
        color: white !important;
        width: 90% !important;
        height: 70px !important;
        font-size: 26px !important;
        font-weight: bold !important;
        margin: 10px auto !important;
        display: block !important;
        border-radius: 15px !important;
    }

    /* Tabel HTML: Locked & Rapi */
    .custom-table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 12px; }
    .custom-table th, .custom-table td { padding: 12px 2px; border-bottom: 1px solid #444; text-align: center; vertical-align: middle; }
    .custom-table th { background-color: #222; color: white; font-size: 11px; }
    .custom-table td.nama-cell { text-align: left; padding-left: 8px; font-weight: bold; font-size: 13px; }
    .custom-table tr:nth-child(even) { background-color: rgba(255,255,255,0.05); }

    /* Tombol P & S Gede & Bulat */
    .btn-container { display: flex; justify-content: center; gap: 8px; }
    .btn-absen {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 42px !important;
        height: 42px !important;
        border-radius: 50% !important;
        text-decoration: none !important;
        font-weight: bold !important;
        font-size: 16px !important;
        color: white !important;
        border: none !important;
    }
    .pagi-on { background-color: #2980b9; box-shadow: 0 0 10px #2980b9; }
    .sore-on { background-color: #e67e22; box-shadow: 0 0 10px #e67e22; }
    .btn-off { background-color: #333; color: #666 !important; pointer-events: none; }
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

# --- LOGIKA WAKTU ---
wita_now = datetime.now() + timedelta(hours=8)
is_pagi_time = wita_now.hour < 11

st.markdown("<h3 class='centered'>📊 MONITORING ABSENSI KPU HSS</h3>", unsafe_allow_html=True)
st.markdown(f"<div class='centered clock-style'>{wita_now.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

# --- CONTROLS ---
tgl_pilihan = st.date_input("Pilih Tanggal", wita_now.date(), label_visibility="collapsed")
if st.button("🔍 CEK ABSEN"): st.rerun()

def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        df.columns = df.columns.str.strip()
        for col in df.columns[:2]: df[col] = pd.to_datetime(df[col], dayfirst=True, errors='ignore')
        return df
    except: return pd.DataFrame()

def render_final_ui(df, master, form_url, prefix):
    t_m, t_s = datetime.strptime("09:00", "%H:%M").time(), datetime.strptime("16:00", "%H:%M").time()
    log = {}
    if not df.empty:
        df_clean = df.copy()
        time_col, name_col = df_clean.columns[0], df_clean.columns[1]
        df_clean[time_col] = pd.to_datetime(df_clean[time_col], errors='coerce')
        df_day = df_clean[df_clean[time_col].dt.date == tgl_pilihan]
        for _, r in df_day.iterrows():
            nama, jam = str(r[name_col]).strip(), r[time_col].time()
            if nama not in log: log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HDR" if jam <= t_m else "TLT"}
            elif jam >= t_s: log[nama]["p"] = jam.strftime("%H:%M")

    # BUILD TABLE
    html = """<table class='custom-table'>
    <tr><th style='width:8%'>#</th><th style='width:38%'>NAMA PEGAWAI</th><th style='width:12%'>PAGI</th>
    <th style='width:12%'>SORE</th><th style='width:10%'>ST</th><th style='width:20%'>ABSEN</th></tr>"""
    
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--", "p": "--", "k": "ALPA"})
        clr = "#2ecc71" if d["k"]=="HDR" else "#e67e22" if d["k"]=="TLT" else "#e74c3c"
        
        # Smart Button Class
        p_class = "pagi-on" if is_pagi_time else "btn-off"
        s_class = "sore-on" if not is_pagi_time else "btn-off"
        
        html += f"""<tr>
            <td>{i}</td><td class='nama-cell'>{p.split(',')[0]}</td><td>{d['m']}</td><td>{d['p']}</td>
            <td style='color:{clr}; font-weight:bold;'>{d['k']}</td>
            <td>
                <div class='btn-container'>
                    <a href='#' class='btn-absen {p_class}'>P</a>
                    <a href='#' class='btn-absen {s_class}'>S</a>
                </div>
            </td>
        </tr>"""
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)
    
    # Hidden Streamlit functionality triggers
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        selected_p = st.selectbox(f"Absen Cepat {prefix.upper()}", ["-- Pilih Nama --"] + sorted(master), key=f"sel_{prefix}")
    with c2:
        label = "PAGI" if is_pagi_time else "SORE"
        if st.button(f"KIRIM {label}", key=f"btn_go_{prefix}"):
            if selected_p != "-- Pilih Nama --":
                requests.post(form_url, data={"entry.960346359": selected_p})
                st.toast(f"✅ {label}: {selected_p} Sukses!")
                time.sleep(0.5); st.rerun()
            else: st.warning("Pilih nama dulu!")

tab1, tab2 = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
with tab1: render_final_ui(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS, "pns")
with tab2: render_final_ui(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK, "pppk")
