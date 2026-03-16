import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import calendar
import pytz
import random
import time
import streamlit.components.v1 as components

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v63.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%); background-attachment: fixed; }
    .block-container { max-width: 1050px; padding-top: 5rem !important; }
    .header-box { text-align: center; color: #F59E0B; font-size: 32px; font-weight: bold; margin-bottom: 5px; }
    .clock-box { text-align: center; color: white; font-size: 18px; margin-bottom: 25px; font-family: monospace; }
    .employee-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); padding: 10px 20px; border-radius: 12px; display: flex; align-items: center; margin-bottom: 5px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .emp-name { flex: 3; color: white; font-weight: bold; font-size: 14px; }
    .emp-time { flex: 1.2; color: #cbd5e1; text-align: center; font-size: 13px; }
    .emp-status { flex: 1; text-align: right; font-weight: bold; font-size: 13px; }
    .status-hadir { color: #10B981; }
    .status-alpa { color: #EF4444; }
    .status-terlambat { color: #F59E0B; }
    .stButton>button { background: rgba(255, 255, 255, 0.1) !important; backdrop-filter: blur(5px); border: 1px solid rgba(255, 255, 255, 0.2) !important; color: white !important; border-radius: 8px; font-weight: bold; }
    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURATION ---
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
URL_LAPKIN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRAsm8AeVaDEUfGHvO95Q4IGSjmd7rDnK1Xt305f5UVrbr6V1TxURbVAnKLCfwv7My_NveJvbK439Wx/pub?output=csv"
SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbz9ZZT3bgQkG52H--yFg-Er8l0OSXNqobbNmKTsx-DV4n2ki2t1uCUlHXSbFahNDOnw/exec"

FORM_ID_PNS = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA"
FORM_ID_PPPK = "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
E_NAMA, E_NIP, E_JABATAN = "entry.960346359", "entry.468881973", "entry.159009649"

DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris KPU", "Sekretariat KPU Kab. Hulu Sungai Selatan", "-", "PNS", "Ketua KPU Kab. HSS", "-"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum dan SDM", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan, Data dan Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan Operasional", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum Dan Perundang- Undangan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum Dan Perundang- Undangan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Sya'bani Rona Baika": ["199202072024212044", "Pranata Komputer Ahli Pertama", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Apriadi Rakhman": ["198904222024211013", "Pranata Komputer Ahli Pertama", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "M Satria Maipadly": ["198905262024211016", "Penata Kelola Pemilu Ahli Pertama", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Basuki Rahmat": ["197705222024211007", "Penata Kelola Pemilu Ahli Pertama", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Sulaiman": ["198411222024211010", "Penata Kelola Pemilu Ahli Pertama", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Saldoz Yedi": ["198008112025211019", "Operator Layanan Operasional", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum and Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Mastoni Ridani": ["199106012025211018", "Operator Layanan Operasional", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum and Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Suriadi": ["199803022025211005", "Pengelola Umum Operasional", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum and Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Ami Aspihani": ["198204042025211031", "Operator Layanan Operasional", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum and Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Abdurrahman": ["198810122025211031", "Staf Subbag Sosdiklih, Parmas and SDM", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Emaliani": ["198906222025212027", "Pengadministrasi Perkantoran", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum and Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "Penata Kelola Pemilu Ahli Pertama", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "Penata Kelola Pemilu Ahli Pertama", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Nadianti": ["199906062025212036", "Pengadministrasi Perkantoran", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"]
}

LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

def get_clean_df(url):
    try:
        r = requests.get(f"{url}&cb={random.random()}", timeout=15)
        return pd.read_csv(StringIO(r.text)).dropna(how='all')
    except: return None

@st.dialog("Update Data Pegawai")
def pop_update(nama):
    st.write(f"Pegawai: **{nama}**")
    tipe = st.radio("Pilih Update:", ["Absen", "Lapkin"])
    info = DATABASE_INFO[nama]
    if tipe == "Absen":
        if st.button("🚀 KIRIM ABSEN SEKARANG"):
            f_id = FORM_ID_PNS if info[4] == "PNS" else FORM_ID_PPPK
            u_nama, u_nip, u_jab = nama.replace(" ", "+"), info[0].replace(" ", "+"), info[1].replace(" ", "+")
            full_url = f"https://docs.google.com/forms/d/e/{f_id}/formResponse?{E_NAMA}={u_nama}&{E_NIP}={u_nip}&{E_JABATAN}={u_jab}&submit=Submit"
            components.html(f"""<iframe name="h" style="display:none;"></iframe><form action="{full_url}" method="post" target="h" id="f"></form><script>document.getElementById('f').submit(); alert('Absen Berhasil!');</script>""", height=0)
            st.success("Terkirim!"); time.sleep(1); st.rerun()
    else:
        st_fix = st.selectbox("Status:", ["Hadir", "Izin", "Sakit", "Tugas Luar", "Cuti"])
        h_kerja = st.text_area("Uraian Hasil Kerja:")
        if st.button("📝 SIMPAN LAPKIN"):
            payload = {"nama": nama, "nip": info[0], "jabatan": info[1], "status": st_fix, "hasil": h_kerja}
            requests.post(SCRIPT_LAPKIN, json=payload)
            st.success("Tersimpan!"); time.sleep(1); st.rerun()

@st.dialog("Download Laporan Bulanan")
def pop_cetak():
    c_b = st.selectbox("Pilih Bulan:", LIST_BULAN, index=datetime.now(wita_tz).month-1)
    c_n = st.selectbox("Pilih Pegawai:", list(DATABASE_INFO.keys()))
    if st.button("📊 GENERATE LAPORAN", use_container_width=True):
        df = get_clean_df(URL_LAPKIN)
        if df is not None:
            df['ts_str'] = df.iloc[:, 0].astype(str)
            m_idx = f"{LIST_BULAN.index(c_b)+1:02d}"
            df_f = df[(df.iloc[:, 1] == c_n) & (df['ts_str'].str.contains(f"/{m_idx}/") | df['ts_str'].str.contains(f"-{m_idx}-"))].copy()
            if not df_f.empty:
                info = DATABASE_INFO[c_n]
                thn_skrg = datetime.now(wita_tz).year
                hr_terakhir = calendar.monthrange(thn_skrg, LIST_BULAN.index(c_b)+1)[1]
                tgl_footer = f"{hr_terakhir} {c_b} {thn_skrg}"
                out = BytesIO()
                with pd.ExcelWriter(out, engine='openpyxl') as writer:
                    header = [["LAPORAN BULANAN"], ["SEKRETARIAT KPU KABUPATEN HULU SUNGAI SELATAN"], [], ["Bulan", f": {c_b}"], ["Nama", f": {c_n}"], ["Jabatan", f": {info[1]}"], ["Unit Kerja", f": {info[2]}"], ["Sub Bagian", f": {info[3]}"], [], ["Hasil Kinerja", ":"], ["No", "Hari / Tanggal", "Uraian Kegiatan", "Hasil Kerja/Output", "Keterangan"]]
                    body = [[i+1, pd.to_datetime(r.iloc[0], dayfirst=True).strftime('%d %B %Y'), f"Melaksanakan Pekerjaan sesuai Tupoksi pada {info[3]} di {info[2]}", r.iloc[5], "-"] for i, (_, r) in enumerate(df_f.iterrows())]
                    # FOOTER SINGLE SIGNATURE (ATASAN LANGSUNG SAJA)
                    footer = [[], ["", "", "", f"Kandangan, {tgl_footer}"], ["", "", "", "Atasan Langsung,"], ["", "", "", "Kepala Sub Bagian," if "Sekretaris" not in info[1] else "Ketua KPU,"], [], [], [], ["", "", "", info[5]], ["", "", "", f"NIP. {info[6]}"]]
                    pd.DataFrame(header).to_excel(writer, index=False, header=False, sheet_name="Laporan")
                    pd.DataFrame(body).to_excel(writer, startrow=11, index=False, header=False, sheet_name="Laporan")
                    pd.DataFrame(footer).to_excel(writer, startrow=11+len(body), index=False, header=False, sheet_name="Laporan")
                st.download_button("📥 DOWNLOAD LAPORAN", out.getvalue(), f"LAPORAN_{c_n}.xlsx", use_container_width=True)
            else: st.warning("Data tidak ditemukan.")

# --- 5. MAIN UI ---
st.markdown('<div class="header-box">🏛️ MONITORING KPU HSS</div>', unsafe_allow_html=True)
st.markdown(f'<div class="clock-box">{datetime.now(wita_tz).strftime("%H:%M:%S WITA")}</div>', unsafe_allow_html=True)
_, mid, _ = st.columns([0.1, 5, 0.1])
with mid:
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a: 
        if st.button("🔄 REFRESH"): st.rerun()
    with col_b: pilih_tgl = st.date_input("Tgl", value=datetime.now(wita_tz).date(), label_visibility="collapsed")
    with col_c: 
        if st.button("📥 REKAP"): 
             df1, df2 = get_clean_df(URL_PNS), get_clean_df(URL_PPPK)
             if df1 is not None:
                 out = BytesIO(); pd.concat([df1, df2]).to_excel(out, index=False)
                 st.download_button("📥 REKAP TOTAL", out.getvalue(), "REKAP.xlsx")
    with col_d: 
        if st.button("🖨️ DOWNLOAD"): pop_cetak()

st.write("---")
tab_all, tab_pns, tab_pppk = st.tabs(["🌎 SEMUA PEGAWAI", "👥 PNS", "👥 PPPK"])

def render_ui(urls, masters, tgl_target, tab_id):
    all_dfs = []
    for u in urls:
        df_t = get_clean_df(u)
        if df_t is not None: all_dfs.append(df_t)
    if not all_dfs: return
    df = pd.concat(all_dfs, ignore_index=True)
    t_str, t_alt = tgl_target.strftime('%d/%m/%Y'), tgl_target.strftime('%Y-%m-%d')
    log = {}
    for _, r in df.iterrows():
        ts = str(r.iloc[0])
        if t_str in ts or t_alt in ts:
            nama = str(r.iloc[1]).strip()
            try:
                dt = pd.to_datetime(ts, dayfirst=True, errors='coerce')
                if pd.isna(dt): continue
                if nama not in log: log[nama] = {"m": dt.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if dt.hour < 9 else "TERLAMBAT"}
                if dt.hour >= 15: log[nama]["p"] = dt.strftime("%H:%M")
            except: continue
    for i, p in enumerate(masters, 1):
        d = log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        st_cls = "status-hadir" if d['k'] == "HADIR" else "status-terlambat" if d['k'] == "TERLAMBAT" else "status-alpa"
        c_main, c_side = st.columns([8.5, 1.5])
        with c_main: st.markdown(f'<div class="employee-card"><div class="emp-name">{i}. {p}</div><div class="emp-time">M: <b>{d["m"]}</b></div><div class="emp-time">P: <b>{d["p"]}</b></div><div class="emp-status {st_cls}">{d["k"]}</div></div>', unsafe_allow_html=True)
        with c_side:
            if st.button("Update", key=f"btn_{p}_{tab_id}"): pop_update(p)

with tab_all: render_ui([URL_PNS, URL_PPPK], list(DATABASE_INFO.keys()), pilih_tgl, "all")
with tab_pns: render_ui([URL_PNS], list(DATABASE_INFO.keys())[:17], pilih_tgl, "pns")
with tab_pppk: render_ui([URL_PPPK], list(DATABASE_INFO.keys())[17:], pilih_tgl, "pppk")
