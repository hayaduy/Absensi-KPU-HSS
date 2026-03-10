import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# 2. CSS CUSTOM
st.markdown("""
    <style>
    .stApp { background-color: #2d0a0a; color: #ffffff; }
    .header-jam { text-align: center; padding: 10px 0; }
    .clock-text { font-size: 60px; font-weight: bold; color: #ffffff; text-shadow: 0 0 20px rgba(255,255,255,0.6); }
    
    /* Baris Pegawai */
    .row-container {
        display: flex; align-items: center;
        background: linear-gradient(90deg, #4c0519 0%, #7f1d1d 100%);
        padding: 15px 25px; border-radius: 15px; margin-bottom: 10px; border: 1px solid #991b1b;
        max-width: 100%; margin-left: auto; margin-right: auto;
    }
    .col-nama { flex: 4; font-size: 18px; font-weight: 700; }
    .col-nama a { color: #fecaca; text-decoration: none; display: block; width: 100%; }
    .col-data-wrap { flex: 5; display: flex; justify-content: space-around; text-align: center; border-left: 1px solid #991b1b; padding: 0 30px; }
    .val-v { font-size: 16px; font-weight: 800; color: #ffffff; }
    .label-k { font-size: 10px; color: #fca5a5; text-transform: uppercase; }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] { background-color: #1a0505 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA MASTER
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
E_ID = "960346359"

# 4. SIDEBAR (MENU & KONTROL)
with st.sidebar:
    st.title("📌 MENU UTAMA")
    menu = st.radio("Pilih Tampilan:", ["👥 Absensi Harian", "📊 Rekap & Sorting"])
    st.divider()
    
    st.subheader("⚙️ Pengaturan")
    tgl_pilihan = st.date_input("Tanggal Data", datetime.now() + timedelta(hours=8))
    
    # SAKLAR AUTO REFRESH
    auto_refresh = st.toggle("Auto Refresh (30s)", value=True)
    
    if st.button("🔄 Refresh Manual", use_container_width=True):
        st.rerun()

# 5. HEADER JAM
wita_now = datetime.now() + timedelta(hours=8)
st.markdown(f'<div class="header-jam"><div class="clock-text">{wita_now.strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

# 6. LOGIKA DATA
@st.cache_data(ttl=30)
def fetch_all():
    try:
        res_pns = requests.get(f"{URL_PNS}&nc={random.random()}", timeout=10)
        res_pppk = requests.get(f"{URL_PPPK}&nc={random.random()}", timeout=10)
        df1 = pd.read_csv(StringIO(res_pns.text))
        df2 = pd.read_csv(StringIO(res_pppk.text))
        df1.iloc[:, 0] = pd.to_datetime(df1.iloc[:, 0], dayfirst=True)
        df2.iloc[:, 0] = pd.to_datetime(df2.iloc[:, 0], dayfirst=True)
        return df1, df2
    except: return pd.DataFrame(), pd.DataFrame()

df_pns, df_pppk = fetch_all()

# --- TAMPILAN 1: ABSENSI HARIAN ---
if menu == "👥 Absensi Harian":
    tab_pns, tab_pppk = st.tabs(["PEGAWAI PNS", "PEGAWAI PPPK"])
    
    def render_harian(df, master, form_url):
        today_str = tgl_pilihan.strftime('%d/%m/%Y')
        log = {}
        if not df.empty:
            mask = df.iloc[:, 0].dt.strftime('%d/%m/%Y') == today_str
            df_t = df[mask]
            for _, r in df_t.iterrows():
                nama, dt = str(r.iloc[1]).strip(), r.iloc[0]
                if nama not in log:
                    stts = "HADIR" if dt.hour < 9 else "TERLAMBAT"
                    log[nama] = {"m": dt.strftime("%H:%M"), "p": "--:--", "k": stts}
                elif dt.hour >= 16: log[nama]["p"] = dt.strftime("%H:%M")
        
        for i, p in enumerate(sorted(master), 1):
            n = p.strip()
            d = log.get(n, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
            
            # Logika tambahan status
            if d["k"] == "BELUM ABSEN":
                if tgl_pilihan < wita_now.date(): d["k"] = "ALPA"
                elif wita_now.hour >= 16: d["k"] = "LAPOR KASUBBAG"
                elif wita_now.hour >= 9: d["k"] = "TERLAMBAT"

            clr = "#4ade80" if d["k"]=="HADIR" else "#60a5fa" if d["k"]=="BELUM ABSEN" else "#fb923c" if d["k"]=="TERLAMBAT" else "#f87171"
            link = f"{form_url}?entry.{E_ID}={p.replace(' ', '+')}&submit=Submit"
            st.markdown(f'<div class="row-container"><div class="col-nama"><a href="{link}" target="_self">{i}. {p.split(",")[0]}</a></div><div class="col-data-wrap"><div class="item-box"><div class="label-k">Pagi</div><div class="val-v">{d["m"]}</div></div><div class="item-box"><div class="label-k">Sore</div><div class="val-v">{d["p"]}</div></div><div class="item-box"><div class="label-k">Ket</div><div style="color:{clr}; font-weight:900;">{d["k"]}</div></div></div></div>', unsafe_allow_html=True)

    with tab_pns: render_harian(df_pns, MASTER_DATA["PNS"], FORM_PNS)
    with tab_pppk: render_harian(df_pppk, MASTER_DATA["PPPK"], FORM_PPPK)

# --- TAMPILAN 2: REKAP & SORTING ---
else:
    st.subheader("📊 Rekapitulasi & Sorting Bulanan")
    c1, c2, c3 = st.columns(3)
    with c1: bln = st.selectbox("Bulan", list(range(1, 13)), index=wita_now.month-1)
    with c2: thn = st.selectbox("Tahun", [2024, 2025, 2026], index=2)
    with c3: s_by = st.selectbox("Urutkan Berdasarkan", ["Total Hadir", "Nama Pegawai", "Terlambat"])

    all_data = pd.concat([df_pns, df_pppk])
    if not all_data.empty:
        rep = all_data[(all_data.iloc[:, 0].dt.month == bln) & (all_data.iloc[:, 0].dt.year == thn)].copy()
        rep['Nama'] = rep.iloc[:, 1].str.strip()
        
        rekap_final = []
        for kat, daftar in MASTER_DATA.items():
            for n in daftar:
                p_data = rep[rep['Nama'] == n.strip()]
                h_tepat = p_data[p_data.iloc[:, 0].dt.hour < 9].iloc[:, 0].dt.date.nunique()
                h_telat = p_data[p_data.iloc[:, 0].dt.hour >= 9].iloc[:, 0].dt.date.nunique()
                rekap_final.append({"Nama Pegawai": n, "Hadir Tepat": h_tepat, "Terlambat": h_telat, "Total Hadir": h_tepat + h_telat})
        
        df_res = pd.DataFrame(rekap_final)
        df_res = df_res.sort_values(by=s_by, ascending=(False if s_by != "Nama Pegawai" else True))
        
        st.dataframe(df_res, use_container_width=True, hide_index=True)
        
        csv = df_res.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Data Rekap (CSV)", data=csv, file_name=f"rekap_{bln}_{thn}.csv", mime="text/csv", use_container_width=True)

# 7. LOGIKA AUTO REFRESH
if auto_refresh:
    time.sleep(30)
    st.rerun()
