import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. SETTING HALAMAN
st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# 2. CSS SEDERHANA & RAPI
st.markdown("""
    <style>
    .stApp { background-color: #1e1e1e; color: #ffffff; }
    .clock-container { text-align: center; padding: 20px; background: #2d2d2d; border-radius: 15px; margin-bottom: 20px; }
    .clock-text { font-size: 50px; font-weight: bold; color: #f97316; }
    .card { background: #2d2d2d; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #f97316; }
    </style>
    """, unsafe_allow_html=True)

# 3. MASTER DATA
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

# 4. SIDEBAR UNTUK MENU
with st.sidebar:
    st.title("⚙️ KONTROL")
    menu = st.radio("Navigasi:", ["🏠 Absensi Hari Ini", "📊 Rekap Bulanan"])
    st.divider()
    auto_refresh = st.toggle("Auto Refresh (30s)", value=True)
    if st.button("🔄 Segarkan Sekarang"): st.rerun()

# 5. JAM WITA
wita_now = datetime.now() + timedelta(hours=8)
st.markdown(f'<div class="clock-container"><div class="clock-text">{wita_now.strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

# 6. AMBIL DATA
@st.cache_data(ttl=20)
def get_data():
    try:
        r1 = requests.get(f"{URL_PNS}&nc={random.random()}").text
        r2 = requests.get(f"{URL_PPPK}&nc={random.random()}").text
        df1 = pd.read_csv(StringIO(r1))
        df2 = pd.read_csv(StringIO(r2))
        df1.iloc[:, 0] = pd.to_datetime(df1.iloc[:, 0], dayfirst=True)
        df2.iloc[:, 0] = pd.to_datetime(df2.iloc[:, 0], dayfirst=True)
        return df1, df2
    except: return pd.DataFrame(), pd.DataFrame()

df_pns, df_pppk = get_data()

# --- TAMPILAN 1: DASHBOARD ---
if menu == "🏠 Absensi Hari Ini":
    tgl = st.date_input("Pilih Tanggal", wita_now.date())
    tpns, tpppk = st.tabs(["PEGAWAI PNS", "PEGAWAI PPPK"])
    
    def tampilkan(df, master):
        log = {}
        if not df.empty:
            df_filtered = df[df.iloc[:, 0].dt.date == tgl]
            for _, r in df_filtered.iterrows():
                nama, dt = str(r.iloc[1]).strip(), r.iloc[0]
                if nama not in log:
                    stts = "HADIR" if dt.hour < 9 else "TERLAMBAT"
                    log[nama] = {"m": dt.strftime("%H:%M"), "p": "--:--", "k": stts}
                elif dt.hour >= 16: log[nama]["p"] = dt.strftime("%H:%M")
        
        for p in sorted(master):
            d = log.get(p.strip(), {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
            # Logika Status
            if d["k"] == "BELUM ABSEN":
                if tgl < wita_now.date(): d["k"] = "ALPA"
                elif wita_now.hour >= 16: d["k"] = "LAPOR KASUBBAG"
                elif wita_now.hour >= 9: d["k"] = "TERLAMBAT"
            
            warna = "#4ade80" if d["k"]=="HADIR" else "#fb923c" if d["k"]=="TERLAMBAT" else "#f87171"
            st.markdown(f'''<div class="card">
                <b>{p}</b><br>
                <small>Masuk: {d['m']} | Pulang: {d['p']} | Status: <span style="color:{warna}">{d['k']}</span></small>
            </div>''', unsafe_allow_html=True)

    with tpns: tampilkan(df_pns, MASTER_DATA["PNS"])
    with tpppk: tampilkan(df_pppk, MASTER_DATA["PPPK"])

# --- TAMPILAN 2: REKAP ---
else:
    st.header("📊 Rekapitulasi Bulanan")
    c1, c2, c3 = st.columns(3)
    bln = c1.selectbox("Bulan", range(1, 13), index=wita_now.month-1)
    thn = c2.selectbox("Tahun", [2024, 2025, 2026], index=2)
    sortir = c3.selectbox("Urutkan", ["Total Hadir", "Nama Pegawai"])

    combined = pd.concat([df_pns, df_pppk])
    if not combined.empty:
        df_m = combined[(combined.iloc[:, 0].dt.month == bln) & (combined.iloc[:, 0].dt.year == thn)]
        res = []
        for _, daftar in MASTER_DATA.items():
            for n in daftar:
                p_data = df_m[df_m.iloc[:, 1].str.strip() == n.strip()]
                h = p_data[p_data.iloc[:, 0].dt.hour < 9].iloc[:, 0].dt.date.nunique()
                t = p_data[p_data.iloc[:, 0].dt.hour >= 9].iloc[:, 0].dt.date.nunique()
                res.append({"Nama Pegawai": n, "Hadir Tepat": h, "Terlambat": t, "Total Hadir": h + t})
        
        final_df = pd.DataFrame(res).sort_values(by=sortir, ascending=(False if sortir != "Nama Pegawai" else True))
        st.dataframe(final_df, use_container_width=True, hide_index=True)
        st.download_button("📥 Download CSV", final_df.to_csv(index=False), f"rekap_{bln}.csv", "text/csv")

if auto_refresh:
    time.sleep(30)
    st.rerun()
