import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. Konfigurasi Halaman & Tema
st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# 2. CSS: Desain Minimalis & Profesional
st.markdown("""
    <style>
    /* Global Style */
    .stApp { background-color: #1e1e1e; color: #e0e0e0; }
    
    /* Header & Clock */
    .main-header { text-align: center; padding-bottom: 20px; }
    .clock-text { font-size: 50px; font-weight: 800; color: #f97316; letter-spacing: 2px; }
    
    /* Card Pegawai */
    .employee-card {
        background: #2d2d2d;
        padding: 15px 25px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-left: 5px solid #f97316;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: transform 0.2s;
    }
    .employee-card:hover { transform: scale(1.01); background: #353535; }
    
    .emp-info { flex: 2; }
    .emp-name { font-size: 18px; font-weight: 600; color: #ffffff; text-decoration: none; }
    .emp-name:hover { color: #fb923c; }
    
    .emp-stats { 
        flex: 3; 
        display: flex; 
        justify-content: space-around; 
        text-align: center;
        border-left: 1px solid #444;
    }
    
    .stat-box { min-width: 80px; }
    .stat-label { font-size: 10px; color: #999; text-transform: uppercase; }
    .stat-val { font-size: 15px; font-weight: 700; color: #ddd; }
    
    /* Status Colors */
    .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 800; }
    
    /* Custom Sidebar */
    [data-testid="stSidebar"] { background-color: #121212 !important; border-right: 1px solid #333; }
    
    /* Streamlit UI Tweak */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #2d2d2d !important; 
        border-radius: 8px 8px 0 0 !important;
        color: #888 !important;
    }
    .stTabs [aria-selected="true"] { background-color: #f97316 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Master Data & Config
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
E_ID = "960346359"

# 4. Sidebar Control (Terorganisir)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/46/KPU_Logo.svg", width=80)
    st.title("Sistem Absensi")
    st.divider()
    
    view_mode = st.radio("Pilih Mode:", ["🏠 Dashboard Harian", "📊 Rekap Bulanan"], label_visibility="collapsed")
    
    st.divider()
    selected_date = st.date_input("Filter Tanggal", datetime.now() + timedelta(hours=8))
    
    auto_refresh = st.toggle("Auto Refresh (30s)", value=True)
    if st.button("🔄 Paksa Refresh"): st.rerun()

# 5. Header: Jam WITA
now_wita = datetime.now() + timedelta(hours=8)
st.markdown(f'<div class="main-header"><div class="clock-text">{now_wita.strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

# 6. Fungsi Data & Render
@st.cache_data(ttl=30)
def load_data():
    try:
        res_pns = requests.get(f"{URL_PNS}&nc={random.random()}", timeout=10)
        res_pppk = requests.get(f"{URL_PPPK}&nc={random.random()}", timeout=10)
        df1 = pd.read_csv(StringIO(res_pns.text))
        df2 = pd.read_csv(StringIO(res_pppk.text))
        df1.iloc[:, 0] = pd.to_datetime(df1.iloc[:, 0], dayfirst=True)
        df2.iloc[:, 0] = pd.to_datetime(df2.iloc[:, 0], dayfirst=True)
        return df1, df2
    except: return pd.DataFrame(), pd.DataFrame()

df_pns, df_pppk = load_data()

# --- MODE 1: DASHBOARD HARIAN ---
if view_mode == "🏠 Dashboard Harian":
    t1, t2 = st.tabs(["👥 PNS", "👥 PPPK"])
    
    def render_cards(df, master, form_url):
        date_str = selected_date.strftime('%d/%m/%Y')
        log = {}
        if not df.empty:
            df_filtered = df[df.iloc[:, 0].dt.strftime('%d/%m/%Y') == date_str]
            for _, r in df_filtered.iterrows():
                nama, dt = str(r.iloc[1]).strip(), r.iloc[0]
                if nama not in log:
                    stts = "HADIR" if dt.hour < 9 else "TERLAMBAT"
                    log[nama] = {"m": dt.strftime("%H:%M"), "p": "--:--", "k": stts}
                elif dt.hour >= 16: log[nama]["p"] = dt.strftime("%H:%M")
        
        for p in sorted(master):
            d = log.get(p.strip(), {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
            
            # Logika Status Akhir
            if d["k"] == "BELUM ABSEN":
                if selected_date < now_wita.date(): d["k"] = "ALPA"
                elif now_wita.hour >= 16: d["k"] = "LAPOR KASUBBAG"
                elif now_wita.hour >= 9: d["k"] = "TERLAMBAT"

            color = "#4ade80" if d["k"]=="HADIR" else "#60a5fa" if d["k"]=="BELUM ABSEN" else "#f97316" if d["k"]=="TERLAMBAT" else "#f87171"
            link = f"{form_url}?entry.{E_ID}={p.replace(' ', '+')}&submit=Submit"
            
            st.markdown(f"""
                <div class="employee-card">
                    <div class="emp-info">
                        <a href="{link}" target="_self" class="emp-name">{p.split(',')[0]}</a>
                    </div>
                    <div class="emp-stats">
                        <div class="stat-box"><div class="stat-label">Pagi</div><div class="stat-val">{d['m']}</div></div>
                        <div class="stat-box"><div class="stat-label">Sore</div><div class="stat-val">{d['p']}</div></div>
                        <div class="stat-box">
                            <div class="stat-label">Status</div>
                            <div style="color:{color}; font-size:13px; font-weight:900;">{d['k']}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with t1: render_cards(df_pns, MASTER_DATA["PNS"], FORM_PNS)
    with t2: render_cards(df_pppk, MASTER_DATA["PPPK"], FORM_PPPK)

# --- MODE 2: REKAP BULANAN ---
else:
    st.subheader("📊 Rekapitulasi Data")
    # Kontrol di atas tabel
    c1, c2, c3 = st.columns([1,1,2])
    with c1: bulan = st.selectbox("Bulan", list(range(1, 13)), index=now_wita.month-1)
    with c2: tahun = st.selectbox("Tahun", [2024, 2025, 2026], index=2)
    with c3: urut = st.selectbox("Urutan", ["Total Hadir", "Nama Pegawai", "Terlambat"])

    all_data = pd.concat([df_pns, df_pppk])
    if not all_data.empty:
        df_month = all_data[(all_data.iloc[:, 0].dt.month == bulan) & (all_data.iloc[:, 0].dt.year == tahun)].copy()
        df_month['Nama'] = df_month.iloc[:, 1].str.strip()
        
        rekap = []
        for kat, daftar in MASTER_DATA.items():
            for n in daftar:
                p_data = df_month[df_month['Nama'] == n.strip()]
                h_tepat = p_data[p_data.iloc[:, 0].dt.hour < 9].iloc[:, 0].dt.date.nunique()
                h_telat = p_data[p_data.iloc[:, 0].dt.hour >= 9].iloc[:, 0].dt.date.nunique()
                rekap.append({"Nama Pegawai": n, "Kategori": kat, "Hadir Tepat": h_tepat, "Terlambat": h_telat, "Total Hadir": h_tepat + h_telat})
        
        final_df = pd.DataFrame(rekap).sort_values(by=urut, ascending=(False if urut != "Nama Pegawai" else True))
        
        st.dataframe(final_df, use_container_width=True, hide_index=True)
        
        # Download di bawah tabel
        csv = final_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Ekspor ke CSV", data=csv, file_name=f"Rekap_{bulan}_{tahun}.csv", use_container_width=True)

# 7. Auto Refresh Logic
if auto_refresh:
    time.sleep(30)
    st.rerun()
