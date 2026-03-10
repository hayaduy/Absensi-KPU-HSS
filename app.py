import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# Konfigurasi Halaman
st.set_page_config(page_title="Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# --- CSS PERBAIKAN: AGAR SEJAJAR PERSIS GAMBAR ---
st.markdown("""
    <style>
    .stApp { background-color: #2d0a0a; color: #ffffff; }
    
    /* Header & Jam */
    .header-jam { text-align: center; padding: 20px 0; }
    .clock-text { font-size: 70px; font-weight: bold; color: #ffffff; }
    
    /* Tombol Cari Data & Date Input */
    div[data-testid="stDateInput"] { width: 300px !important; margin: 0 auto !important; }
    .stButton > button { margin: 0 auto !important; }

    /* --- LAYOUT BARIS ABSENSI --- */
    /* Container utama baris menggunakan Streamlit Column agar button berfungsi normal */
    [data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Styling Box Baris */
    .row-card {
        background: linear-gradient(90deg, #3d0808 0%, #4c0519 100%);
        border: 1px solid #5a0c0c;
        border-radius: 12px;
        padding: 15px 25px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        width: 100%;
    }

    .nama-box { flex: 2; font-size: 18px; font-weight: bold; color: #fecaca; }
    
    /* Data Tengah (Pagi, Sore, Ket) */
    .data-section { 
        flex: 3; 
        display: flex; 
        justify-content: space-around; 
        border-left: 1px solid #5a0c0c; 
        padding-left: 20px;
    }
    
    .data-item { text-align: center; }
    .data-label { font-size: 10px; color: #fca5a5; text-transform: uppercase; margin-bottom: 2px; }
    .data-val { font-size: 16px; font-weight: 800; color: #ffffff; }

    /* Overriding Tombol ABSEN agar lonjong & orange gelap */
    .stButton > button {
        background: linear-gradient(90deg, #b43a1a 0%, #8a2a10 100%) !important;
        color: white !important;
        border-radius: 15px !important;
        border: 1px solid #f97316 !important;
        width: 100% !important;
        height: 50px !important;
        font-weight: bold !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] { justify-content: center !important; }
    .stTabs [data-baseweb="tab"] { background-color: #4c0519 !important; }
    .stTabs [aria-selected="true"] { background-color: #f97316 !important; }

    </style>
    """, unsafe_allow_html=True)

# ... (Master Data & Fetch Data tetap sama seperti kode Anda) ...

def render_list(df, master, form_url, prefix):
    t_limit, t_pulang = datetime.strptime("09:00", "%H:%M").time(), datetime.strptime("16:00", "%H:%M").time()
    log = {}
    
    if not df.empty:
        t_str, t_str_alt = tgl_pilihan.strftime('%d/%m/%Y'), tgl_pilihan.strftime('%Y-%m-%d')
        for _, r in df.iterrows():
            ts = str(r.iloc[0])
            if t_str in ts or t_str_alt in ts:
                try:
                    dt = pd.to_datetime(ts, dayfirst=True)
                    nama, jam = str(r.iloc[1]).strip(), dt.time()
                    if nama not in log:
                        log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam <= t_limit else "TERLAMBAT"}
                    elif jam >= t_pulang: log[nama]["p"] = jam.strftime("%H:%M")
                except: continue

    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--:--", "p": "--:--", "k": "ALPA"})
        clr_status = "#4ade80" if d["k"]=="HADIR" else "#fb923c" if d["k"]=="TERLAMBAT" else "#f87171"
        
        # --- PERUBAHAN UTAMA: MENGGUNAKAN COLUMNS UNTUK MEMBUNGKUS CSS ---
        # Kita bagi layout jadi 2 kolom: (1) Data Gabungan, (2) Tombol
        col_info, col_btn = st.columns([8, 2])
        
        with col_info:
            st.markdown(f"""
                <div class="row-card">
                    <div class="nama-box">{i}. {p.split(',')[0]}</div>
                    <div class="data-section">
                        <div class="data-item"><div class="data-label">Pagi</div><div class="data-val">{d['m']}</div></div>
                        <div class="data-item"><div class="data-label">Sore</div><div class="data-val">{d['p']}</div></div>
                        <div class="data-item"><div class="data-label">Ket</div><div style="color:{clr_status}; font-weight:900;">{d['k']}</div></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col_btn:
            # Button diletakkan di dalam kolom kedua agar sejajar secara vertikal dengan row-card
            if st.button("ABSEN", key=f"btn_{prefix}_{i}"):
                direct_submit(form_url, p)

# ... (Panggil Tabs tetap sama) ...
