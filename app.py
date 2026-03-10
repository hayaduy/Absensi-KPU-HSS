import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. TOTAL UI OVERHAUL (SISTEM GRID & CARD MODERN)
st.set_page_config(page_title="KPU HSS - MONITORING", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Reset & Background */
    .stApp { background: #0f172a; color: #f1f5f9; }
    
    /* Global Card Style */
    .status-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .status-card:hover { transform: translateY(-5px); border-color: #f59e0b; }
    
    /* Typography */
    .emp-name-title { font-size: 1.1rem; font-weight: 700; color: #f8fafc; margin-bottom: 10px; height: 50px; overflow: hidden; }
    .time-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
    .time-value { font-size: 1.2rem; font-weight: 800; color: #ffffff; margin-bottom: 15px; }
    
    /* Status Badges */
    .badge { padding: 6px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: 800; display: inline-block; width: 100%; }
    .bg-hadir { background: #059669; color: #ecfdf5; }
    .bg-telat { background: #d97706; color: #fffbeb; }
    .bg-alpa { background: #dc2626; color: #fef2f2; }
    .bg-lapor { background: #7c3aed; color: #f5f3ff; }
    .bg-belum { background: #475569; color: #f1f5f9; }

    /* Clock Header */
    .hero-section { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 30px; border-radius: 20px; border-bottom: 4px solid #f59e0b; margin-bottom: 30px; text-align: center; }
    .main-clock { font-size: 4rem; font-weight: 900; color: #f59e0b; text-shadow: 0 0 20px rgba(245,158,11,0.3); }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #334155; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONFIG & MASTER DATA
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
E_ID = "960346359"

# 3. SIDEBAR NAVIGATION
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/46/KPU_Logo.svg", width=100)
    st.title("Absensi Hub")
    app_mode = st.selectbox("Navigasi Utama", ["🏠 Real-Time Monitor", "📊 Statistik & Rekap"])
    st.divider()
    target_date = st.date_input("Tanggal Pantau", datetime.now() + timedelta(hours=8))
    is_auto = st.checkbox("🔄 Auto Update (30s)", value=True)
    if st.button("🚀 Ambil Data Terbaru", use_container_width=True): st.rerun()

# 4. DATA ENGINE
@st.cache_data(ttl=20)
def get_live_data():
    try:
        r1 = requests.get(f"{URL_PNS}&nc={random.random()}", timeout=10).text
        r2 = requests.get(f"{URL_PPPK}&nc={random.random()}", timeout=10).text
        d1, d2 = pd.read_csv(StringIO(r1)), pd.read_csv(StringIO(r2))
        d1.iloc[:, 0] = pd.to_datetime(d1.iloc[:, 0], dayfirst=True)
        d2.iloc[:, 0] = pd.to_datetime(d2.iloc[:, 0], dayfirst=True)
        return d1, d2
    except: return pd.DataFrame(), pd.DataFrame()

df_pns, df_pppk = get_live_data()
wita_now = datetime.now() + timedelta(hours=8)

# 5. HEADER CLOCK
st.markdown(f'''
    <div class="hero-section">
        <div class="time-label" style="color:#f59e0b">Waktu Indonesia Tengah (WITA)</div>
        <div class="main-clock">{wita_now.strftime("%H:%M:%S")}</div>
        <div style="color:#94a3b8">{wita_now.strftime("%A, %d %B %Y")}</div>
    </div>
''', unsafe_allow_html=True)

# 6. APP LOGIC
if app_mode == "🏠 Real-Time Monitor":
    cat_tab = st.radio("Kategori Pegawai", ["PNS", "PPPK"], horizontal=True, label_visibility="collapsed")
    
    # Grid Rendering
    master_list = MASTER_DATA[cat_tab]
    current_df = df_pns if cat_tab == "PNS" else df_pppk
    f_url = FORM_PNS if cat_tab == "PNS" else FORM_PPPK
    
    # Logika Pencocokan
    status_map = {}
    if not current_df.empty:
        today_data = current_df[current_df.iloc[:, 0].dt.date == target_date]
        for _, row in today_data.iterrows():
            name, ts = str(row.iloc[1]).strip(), row.iloc[0]
            if name not in status_map:
                stts = "HADIR" if ts.hour < 9 else "TERLAMBAT"
                status_map[name] = {"in": ts.strftime("%H:%M"), "out": "--:--", "ket": stts}
            elif ts.hour >= 16: status_map[name]["out"] = ts.strftime("%H:%M")

    # Display Grid
    cols = st.columns(4) # Menampilkan 4 kartu per baris
    for idx, name in enumerate(sorted(master_list)):
        data = status_map.get(name.strip(), {"in": "--:--", "out": "--:--", "ket": "BELUM ABSEN"})
        
        # Penyesuaian Status
        if data["ket"] == "BELUM ABSEN":
            if target_date < wita_now.date(): data["ket"] = "ALPA"
            elif wita_now.hour >= 16: data["ket"] = "LAPOR KASUBBAG"
            elif wita_now.hour >= 9: data["ket"] = "TERLAMBAT"
            
        b_class = "bg-hadir" if data["ket"]=="HADIR" else "bg-telat" if data["ket"]=="TERLAMBAT" else "bg-alpa" if data["ket"]=="ALPA" else "bg-lapor" if data["ket"]=="LAPOR KASUBBAG" else "bg-belum"
        l_form = f"{f_url}?entry.{E_ID}={name.replace(' ', '+')}&submit=Submit"
        
        with cols[idx % 4]:
            st.markdown(f'''
                <div class="status-card">
                    <div class="emp-name-title"><a href="{l_form}" target="_self" style="color:inherit; text-decoration:none;">{name.split(',')[0]}</a></div>
                    <div class="time-label">Masuk</div>
                    <div class="time-value">{data['in']}</div>
                    <div class="time-label">Pulang</div>
                    <div class="time-value">{data['out']}</div>
                    <div class="badge {b_class}">{data['ket']}</div>
                </div>
            ''', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

else:
    st.subheader("📊 Rekapitulasi & Urutan")
    c1, c2, c3 = st.columns(3)
    sel_b = c1.selectbox("Bulan", range(1, 13), index=wita_now.month-1)
    sel_t = c2.selectbox("Tahun", [2024, 2025, 2026], index=2)
    sel_s = c3.selectbox("Urutkan Berdasarkan", ["Total Hadir", "Nama Pegawai", "Terlambat"])

    combined = pd.concat([df_pns, df_pppk])
    if not combined.empty:
        df_m = combined[(combined.iloc[:, 0].dt.month == sel_b) & (combined.iloc[:, 0].dt.year == sel_t)]
        rekap_res = []
        for kat, daftar in MASTER_DATA.items():
            for n in daftar:
                p_data = df_m[df_m.iloc[:, 1].str.strip() == n.strip()]
                h = p_data[p_data.iloc[:, 0].dt.hour < 9].iloc[:, 0].dt.date.nunique()
                t = p_data[p_data.iloc[:, 0].dt.hour >= 9].iloc[:, 0].dt.date.nunique()
                rekap_res.append({"Nama Pegawai": n, "Kategori": kat, "Hadir Tepat": h, "Terlambat": t, "Total Hadir": h + t})
        
        final_df = pd.DataFrame(rekap_res).sort_values(by=sel_s, ascending=(False if sel_s != "Nama Pegawai" else True))
        st.dataframe(final_df, use_container_width=True, hide_index=True)
        st.download_button("📥 Ekspor Laporan CSV", final_df.to_csv(index=False), f"rekap_{sel_b}.csv", "text/csv", use_container_width=True)

# 7. REFRESH ENGINE
if is_auto:
    time.sleep(30)
    st.rerun()
