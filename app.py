import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# 2. CSS: SEDERHANA, MODERN, & ORGANIZED
st.markdown("""
    <style>
    .stApp { background-color: #1a1a1a; color: #ffffff; }
    .clock-container { text-align: center; padding: 20px; background: #2d2d2d; border-radius: 15px; margin-bottom: 25px; border: 1px solid #444; }
    .clock-text { font-size: 50px; font-weight: bold; color: #f97316; text-shadow: 0 0 10px rgba(249,115,22,0.3); }
    
    /* Card Style untuk Pegawai */
    .emp-card { 
        background: #2d2d2d; 
        padding: 18px; 
        border-radius: 12px; 
        margin-bottom: 12px; 
        border-left: 6px solid #f97316;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .emp-name { font-size: 18px; font-weight: bold; color: #ffffff; text-decoration: none; }
    .emp-name:hover { color: #f97316; }
    .status-badge { font-weight: 900; font-size: 14px; text-transform: uppercase; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #121212 !important; border-right: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# 3. MASTER DATA
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
E_ID = "960346359"

# 4. SIDEBAR (KONTROL UTAMA)
with st.sidebar:
    st.title("📌 MENU")
    menu = st.radio("Pilih Tampilan:", ["🏠 Absensi Hari Ini", "📊 Rekap & Sorting"])
    st.divider()
    
    st.subheader("⚙️ Opsi")
    # SAKLAR AUTO REFRESH
    auto_refresh = st.toggle("Aktifkan Auto Refresh", value=True)
    if st.button("🔄 Segarkan Manual", use_container_width=True):
        st.rerun()
    
    st.divider()
    st.caption("v2.1 - KPU HSS")

# 5. JAM DIGITAL (WITA)
wita_now = datetime.now() + timedelta(hours=8)
st.markdown(f'<div class="clock-container"><div class="clock-text">{wita_now.strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

# 6. FUNGSI LOAD DATA
@st.cache_data(ttl=30)
def load_data():
    try:
        r1 = requests.get(f"{URL_PNS}&nc={random.random()}", timeout=10).text
        r2 = requests.get(f"{URL_PPPK}&nc={random.random()}", timeout=10).text
        df1 = pd.read_csv(StringIO(r1))
        df2 = pd.read_csv(StringIO(r2))
        df1.iloc[:, 0] = pd.to_datetime(df1.iloc[:, 0], dayfirst=True)
        df2.iloc[:, 0] = pd.to_datetime(df2.iloc[:, 0], dayfirst=True)
        return df1, df2
    except: return pd.DataFrame(), pd.DataFrame()

df_pns, df_pppk = load_data()

# 7. LOGIKA MENU
if menu == "🏠 Absensi Hari Ini":
    tgl_pilih = st.date_input("Filter Tanggal", wita_now.date())
    tab_pns, tab_pppk = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
    
    # FUNGSI UNTUK MERENDER DAFTAR (PENGGANTI render_list)
    def render_view(df, master, form_url):
        log = {}
        if not df.empty:
            mask = df.iloc[:, 0].dt.date == tgl_pilih
            df_filtered = df[mask]
            for _, r in df_filtered.iterrows():
                nama, dt = str(r.iloc[1]).strip(), r.iloc[0]
                if nama not in log:
                    stts = "HADIR" if dt.hour < 9 else "TERLAMBAT"
                    log[nama] = {"m": dt.strftime("%H:%M"), "p": "--:--", "k": stts}
                elif dt.hour >= 16: log[nama]["p"] = dt.strftime("%H:%M")
        
        for p in sorted(master):
            n = p.strip()
            d = log.get(n, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
            
            # Logika Status Otomatis
            if d["k"] == "BELUM ABSEN":
                if tgl_pilih < wita_now.date(): d["k"] = "ALPA"
                elif wita_now.hour >= 16: d["k"] = "LAPOR KASUBBAG"
                elif wita_now.hour >= 9: d["k"] = "TERLAMBAT"

            clr = "#4ade80" if d["k"]=="HADIR" else "#60a5fa" if d["k"]=="BELUM ABSEN" else "#fb923c" if d["k"]=="TERLAMBAT" else "#f87171"
            link = f"{form_url
