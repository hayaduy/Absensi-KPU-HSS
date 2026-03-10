import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- CSS TOTAL FIX: ZEBRA & MOBILE ALIGNMENT ---
st.markdown("""
    <style>
    /* Paksa container utama rata tengah */
    .main-control {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Tombol Cek Absen di Tengah */
    div.stButton > button:first-child {
        background-color: #d35400 !important;
        color: white !important;
        width: 250px !important;
        height: 50px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        margin: 0 auto !important;
        display: block !important;
    }

    /* Memperbesar Tab Jenis Pegawai */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center !important;
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 18px !important;
        font-weight: bold !important;
    }

    /* Tabel HTML Custom agar lurus di HP */
    .absen-table {
        width: 100%;
        border-collapse: collapse;
        font-family: sans-serif;
        font-size: 13px;
    }
    .absen-table th {
        background-color: #333;
        padding: 10px 5px;
        text-align: left;
        color: white;
    }
    .absen-table td {
        padding: 8px 5px;
        border-bottom: 1px solid #444;
    }
    /* Zebra Stripes */
    .absen-table tr:nth-child(even) {
        background-color: rgba(255, 255, 255, 0.05);
    }
    
    /* Tombol Absen di Tabel */
    .btn-absen {
        background-color: #2980b9;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 11px;
        font-weight: bold;
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

# --- HEADER & JAM ---
wita_now = datetime.now() + timedelta(hours=8)
st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>📊 MONITORING ABSENSI KPU HSS</h2>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align: center; color: #3498db; font-size: 50px; margin-top: 0;'>{wita_now.strftime('%H:%M:%S')}</h1>", unsafe_allow_html=True)

# --- KONTROL TENGAH ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    tgl_pilihan = st.date_input("Tanggal", wita_now.date(), label_visibility="collapsed")
    if st.button("🔍 CEK ABSEN"):
        st.rerun()

def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        df.columns = df.columns.str.strip()
        for col in df.columns[:2]:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors='ignore')
        return df
    except: return pd.DataFrame()

def display_absen(df, master, form_url):
    t_limit = datetime.strptime("09:00", "%H:%M").time()
    t_pulang = datetime.strptime("16:00", "%H:%M").time()
    log = {}
    
    if not df.empty:
        df_clean = df.copy()
        time_col, name_col = df_clean.columns[0], df_clean.columns[1]
        df_clean[time_col] = pd.to_datetime(df_clean[time_col], errors='coerce')
        df_clean = df_clean.dropna(subset=[time_col])
        df_day = df_clean[df_clean[time_col].dt.date == tgl_pilihan]
        for _, r in df_day.iterrows():
            nama, jam = str(r[name_col]).strip(), r[time_col].time()
            if nama not in log:
                log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam <= t_limit else "TERLAMBAT"}
            elif jam >= t_pulang:
                log[nama]["p"] = jam.strftime("%H:%M")

    # BANGUN TABEL HTML (Agar Lurus & Ada Zebra)
    html_table = "<table class='absen-table'><tr><th>#</th><th>NAMA PEGAWAI</th><th>M</th><th>P</th><th>ST</th></tr>"
    
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--:--", "p": "--:--", "k": "❌"})
        color = "#2ecc71" if "HADIR" in d["k"] else "#e67e22" if "TERLAMBAT" in d["k"] else "#e74c3c"
        st_label = "HDR" if "HADIR" in d["k"] else "TLT" if "TERLAMBAT" in d["k"] else "ALPA"
        
        html_table += f"""
        <tr>
            <td>{i}</td>
            <td><b>{p}</b></td>
            <td>{d['m']}</td>
            <td>{d['p']}</td>
            <td style='color: {color}; font-weight: bold;'>{st_label}</td>
        </tr>
        """
    html_table += "</table>"
    st.markdown(html_table, unsafe_allow_html=True)
    
    # Tombol Absen ditaruh di bawah tabel dalam kolom yang rapi
    st.write("---")
    st.write("**AKSI CEPAT (KLIK NAMA):**")
    cols = st.columns(2) # Bagi 2 kolom tombol biar gak melar
    for i, p in enumerate(sorted(master)):
        with cols[i % 2]:
            if st.button(f"ABSEN: {p.split(',')[0]}", key=f"btn_{p}_{i}"):
                requests.post(form_url, data={"entry.960346359": p})
                st.toast(f"✅ {p} Sukses!")
                time.sleep(0.5)
                st.rerun()

tab1, tab2 = st.tabs(["👥 PNS", "👥 PPPK"])
with tab1: display_absen(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS)
with tab2: display_absen(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK)
