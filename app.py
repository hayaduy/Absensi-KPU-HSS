import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time
import random

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- DATA MASTER (Otak v3.2) ---
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"

# --- JAM DIGITAL ---
st.markdown(f"<h1 style='text-align: center;'>📊 MONITORING ABSENSI KPU HSS</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center; color: #3498db;'>🕒 {datetime.now().strftime('%H:%M:%S')}</h3>", unsafe_allow_html=True)

# --- CONTROLS ---
col_tgl, col_btn = st.columns([2, 1])
with col_tgl:
    tgl_pilihan = st.date_input("📅 Pilih Tanggal Scan/Absen", datetime.now())
with col_btn:
    if st.button("🔍 SCAN DATA SEKARANG", use_container_width=True):
        st.rerun()

# --- FUNGSI ---
def fetch_data(url):
    try:
        res = requests.get(f"{url}&nocache={random.random()}", timeout=10)
        df = pd.read_csv(requests.compat.StringIO(res.text))
        df.columns = df.columns.str.strip()
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
        return df.dropna(subset=[df.columns[0]])
    except: return pd.DataFrame()

def proses_absen(nama, url):
    # Gunakan ID Tanggal jika ingin Backdate, di sini pakai standar Nama dulu
    payload = {"entry.960346359": nama, "entry.111111111": tgl_pilihan.strftime('%d/%m/%Y')}
    requests.post(url, data=payload)
    st.toast(f"✅ Absensi {nama} Terkirim!")
    time.sleep(1)
    st.rerun()

# --- TABEL ---
tab_pns, tab_pppk = st.tabs(["PEGAWAI PNS", "PEGAWAI PPPK"])

def draw_ui(df, master, form_url):
    t_limit = datetime.strptime("09:00", "%H:%M").time()
    t_pulang = datetime.strptime("16:00", "%H:%M").time()
    log = {}
    
    if not df.empty:
        tgl_str = tgl_pilihan.strftime('%d/%m/%Y')
        col_tgl = [c for c in df.columns if 'Tanggal' in c]
        df_day = df[df[col_tgl[0]] == tgl_str] if col_tgl else df[df.iloc[:, 0].dt.date == tgl_pilihan]
        df_day = df_day.sort_values(by=df.columns[0])
        
        for _, r in df_day.iterrows():
            nama = str(r.iloc[1]).strip()
            jam = r.iloc[0].time()
            if nama not in log:
                log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam <= t_limit else "TERLAMBAT"}
            elif jam >= t_pulang:
                log[nama]["p"] = jam.strftime("%H:%M")

    # Header
    c1, c2, c3, c4, c5, c6 = st.columns([0.5, 3, 1, 1, 1.5, 1])
    c1.write("**NO**"); c2.write("**NAMA PEGAWAI**"); c3.write("**MASUK**"); c4.write("**PULANG**"); c5.write("**STATUS**"); c6.write("**AKSI**")
    st.divider()

    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--:--", "p": "--:--", "k": "❌ ALPA"})
        r1, r2, r3, r4, r5, r6 = st.columns([0.5, 3, 1, 1, 1.5, 1])
        r1.write(str(i))
        r2.write(f"**{p}**")
        r3.write(d["m"])
        r4.write(d["p"])
        color = "green" if "HADIR" in d["k"] else "orange" if "TERLAMBAT" in d["k"] else "red"
        r5.markdown(f":{color}[{d['k']}]")
        if r6.button("ABSEN", key=f"btn_{p}_{i}"):
            proses_absen(p, form_url)

with tab_pns:
    draw_ui(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS)
with tab_pppk:
    draw_ui(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK)
