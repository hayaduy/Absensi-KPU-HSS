import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. TEMA & UI
st.set_page_config(page_title="MONITORING KPU HSS", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #ffffff; }
    .hero { background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 30px; border-radius: 20px; text-align: center; border-bottom: 5px solid #f59e0b; margin-bottom: 30px; }
    .clock { font-size: 60px; font-weight: 900; color: #f59e0b; margin: 0; }
    
    /* Grid Kartu */
    .card-container { display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; }
    .card { background: #1e293b; border: 1px solid #334155; border-radius: 15px; padding: 20px; width: 250px; text-align: center; }
    .card:hover { border-color: #f59e0b; transform: translateY(-3px); transition: 0.3s; }
    
    .name { font-size: 16px; font-weight: 700; color: #f8fafc; margin-bottom: 10px; height: 40px; display: flex; align-items: center; justify-content: center; }
    .time-val { font-size: 20px; font-weight: 800; color: #ffffff; }
    .badge { padding: 5px 10px; border-radius: 8px; font-size: 12px; font-weight: 800; margin-top: 10px; display: block; }
    
    .status-hadir { background: #059669; }
    .status-terlambat { background: #d97706; }
    .status-lapor { background: #7c3aed; }
    .status-alpa { background: #dc2626; }
    .status-belum { background: #475569; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATA
MASTER = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hiyati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

# 3. SIDEBAR
with st.sidebar:
    st.title("📌 MENU")
    nav = st.radio("Navigasi", ["🏠 Dashboard", "📊 Laporan Bulanan", "📅 Detail Harian (Sorting)"])
    st.divider()
    tgl_sidebar = st.date_input("Pilih Tanggal", datetime.now() + timedelta(hours=8))
    refresh = st.toggle("Auto Refresh (30s)", value=True)
    if st.button("🚀 PAKSA UPDATE DATA"): st.rerun()

# 4. LOAD DATA
@st.cache_data(ttl=20)
def load_data():
    try:
        r1 = requests.get(f"{URL_PNS}&nc={random.random()}").text
        r2 = requests.get(f"{URL_PPPK}&nc={random.random()}").text
        d1 = pd.read_csv(StringIO(r1))
        d2 = pd.read_csv(StringIO(r2))
        d1.iloc[:, 0] = pd.to_datetime(d1.iloc[:, 0], dayfirst=True)
        d2.iloc[:, 0] = pd.to_datetime(d2.iloc[:, 0], dayfirst=True)
        return d1, d2
    except: return pd.DataFrame(), pd.DataFrame()

df_pns, df_pppk = load_data()
wita = datetime.now() + timedelta(hours=8)

# 5. HEADER
st.markdown(f'<div class="hero"><div class="clock">{wita.strftime("%H:%M:%S")}</div><div style="color:#94a3b8">{wita.strftime("%A, %d %B %Y")}</div></div>', unsafe_allow_html=True)

# --- DASHBOARD MODE ---
if nav == "🏠 Dashboard":
    kat = st.radio("Kategori", ["PNS", "PPPK"], horizontal=True)
    target_master = MASTER[kat]
    target_df = df_pns if kat == "PNS" else df_pppk
    
    status_db = {}
    if not target_df.empty:
        df_today = target_df[target_df.iloc[:, 0].dt.date == tgl_sidebar]
        for _, r in df_today.iterrows():
            nm, ts = str(r.iloc[1]).strip(), r.iloc[0]
            if nm not in status_db:
                stts = "HADIR" if ts.hour < 9 else "TERLAMBAT"
                status_db[nm] = {"m": ts.strftime("%H:%M"), "p": "--:--", "k": stts}
            elif ts.hour >= 16: status_db[nm]["p"] = ts.strftime("%H:%M")

    grid_html = '<div class="card-container">'
    for nm in sorted(target_master):
        d = status_db.get(nm.strip(), {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
        
        if d["k"] == "BELUM ABSEN":
            if tgl_sidebar < wita.date(): d["k"] = "ALPA"
            elif wita.hour >= 16: d["k"] = "LAPOR KASUBBAG"
            elif wita.hour >= 9: d["k"] = "TERLAMBAT"
        
        # Mapping class CSS
        cls_key = d["k"].lower().split()[0]
        grid_html += f"""
        <div class="card">
            <div class="name">{nm.split(',')[0]}</div>
            <div style="font-size:10px; color:#94a3b8">Masuk</div><div class="time-val">{d['m']}</div>
            <div style="font-size:10px; color:#94a3b8">Pulang</div><div class="time-val">{d['p']}</div>
            <div class="badge status-{cls_key}">{d['k']}</div>
        </div>
        """
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

# --- LAPORAN BULANAN (REKAP) ---
elif nav == "📊 Laporan Bulanan":
    st.subheader("Rekap Kehadiran Bulanan")
    col1, col2, col3 = st.columns([1, 1, 2])
    bulan = col1.selectbox("Bulan", range(1, 13), index=wita.month-1)
    tahun = col2.selectbox("Tahun", [2024, 2025, 2026], index=2)
    sort_opt = col3.selectbox("Urutkan Berdasarkan", ["Total Terbanyak", "Nama (A-Z)"])
    
    full_df = pd.concat([df_pns, df_pppk])
    if not full_df.empty:
        df_m = full_df[(full_df.iloc[:, 0].dt.month == bulan) & (full_df.iloc[:, 0].dt.year == tahun)]
        rkp = []
        for kat, l_nm in MASTER.items():
            for n in l_nm:
                dp = df_m[df_m.iloc[:, 1].str.strip() == n.strip()]
                h = dp[dp.iloc[:, 0].dt.hour < 9].iloc[:, 0].dt.date.nunique()
                tl = dp[dp.iloc[:, 0].dt.hour >= 9].iloc[:, 0].dt.date.nunique()
                rkp.append({"Nama": n, "Kategori": kat, "Hadir Tepat": h, "Terlambat": tl, "Total": h+tl})
        
        res_df = pd.DataFrame(rkp)
        
        # Logika Sorting
        if sort_opt == "Total Terbanyak":
            res_df = res_df.sort_values(by="Total", ascending=False)
        else:
            res_df = res_df.sort_values(by="Nama", ascending=True)
            
        st.dataframe(res_df, use_container_width=True, hide_index=True)

# --- DETAIL HARIAN (SORTING BY NAME & DATE) ---
elif nav == "📅 Detail Harian (Sorting)":
    st.subheader("Data Mentah Absensi (Sorting Nama & Tanggal)")
    
    full_df = pd.concat([df_pns, df_pppk])
    if not full_df.empty:
        # Menyesuaikan nama kolom agar lebih enak dibaca
        clean_df = full_df.copy()
        clean_df.columns = ['Timestamp', 'Nama', 'Keterangan', 'Lokasi'] # Sesuaikan dengan urutan kolom sheet Anda
        
        # Widget Sorting
        c1, c2 = st.columns(2)
        sort_col = c1.selectbox("Urutkan Kolom", ["Timestamp", "Nama"])
        sort_order = c2.radio("Order", ["Terbaru/Z-A", "Terlama/A-Z"], horizontal=True)
        
        ascending = True if sort_order == "Terlama/A-Z" else False
        
        # Eksekusi Sorting
        sorted_df = clean_df.sort_values(by=sort_col, ascending=ascending)
        
        # Tampilkan
        st.dataframe(sorted_df, use_container_width=True, hide_index=True)

# 6. REFRESH
if refresh:
    time.sleep(30)
    st.rerun()
