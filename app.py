import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from io import StringIO
import random
import time

st.set_page_config(page_title="Monitoring Absensi", layout="wide")

# ===================== CSS =====================
st.markdown("""
<style>

.block-container{
padding-top:2rem;
}

.title{
text-align:center;
font-size:32px;
font-weight:700;
}

.clock{
text-align:center;
font-size:50px;
color:#3498db;
margin-bottom:20px;
}

.stat-box{
background:#111;
padding:15px;
border-radius:10px;
text-align:center;
border:1px solid #333;
}

.stat-number{
font-size:26px;
font-weight:700;
}

.stat-label{
font-size:14px;
color:#aaa;
}

.badge-hadir{
color:#2ecc71;
font-weight:bold;
}

.badge-telat{
color:#f39c12;
font-weight:bold;
}

.badge-alpa{
color:#e74c3c;
font-weight:bold;
}

.stButton button{
width:40px;
height:40px;
border-radius:50%;
font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ===================== MASTER DATA =====================
MASTER = [
"Suwanto",
"Wawan Setiawan",
"Ineke Setiyaningsih",
"Farah Agustina Setiawati",
"Rusma Ariati",
"Sya'bani Rona Baika",
"Apriadi Rakhman",
"M Satria Maipadly",
"Basuki Rahmat",
"Sulaiman",
"Saldoz Yedi",
"Mastoni Ridani",
"Suriadi"
]

# ===================== URL =====================
CSV_URL = "CSV_LINK_KAMU"
FORM_URL = "FORM_LINK_KAMU"
ENTRY_ID = "entry.960346359"

# ===================== TIME =====================
now = datetime.now() + timedelta(hours=8)

st.markdown("<div class='title'>MONITORING ABSENSI KPU HSS</div>", unsafe_allow_html=True)

st.markdown(
f"<div class='clock'>{now.strftime('%H:%M:%S')}</div>",
unsafe_allow_html=True
)

tanggal = st.date_input("Tanggal", now.date())

# ===================== FETCH DATA =====================
def fetch_data():

    try:

        r = requests.get(f"{CSV_URL}&cache={random.random()}")

        df = pd.read_csv(StringIO(r.text))

        df.columns = df.columns.str.strip()

        return df

    except:

        return pd.DataFrame()

# ===================== SUBMIT ABSENSI =====================
def kirim_absen(nama):

    payload = {ENTRY_ID:nama}

    headers = {"User-Agent":"Mozilla/5.0"}

    r = requests.post(FORM_URL,data=payload,headers=headers)

    if r.status_code == 200:

        st.toast("Absensi berhasil")

        time.sleep(1)

        st.rerun()

    else:

        st.error("Gagal kirim ke Google Form")

# ===================== PROSES DATA =====================
def proses(df):

    batas = datetime.strptime("09:00","%H:%M").time()

    log = {}

    if not df.empty:

        for _,r in df.iterrows():

            try:

                ts = pd.to_datetime(r.iloc[0],dayfirst=True)

                nama = str(r.iloc[1]).strip()

                if ts.date() == tanggal:

                    jam = ts.time()

                    status = "HDR" if jam <= batas else "TLT"

                    log[nama] = {
                    "masuk":jam.strftime("%H:%M"),
                    "pulang":"--",
                    "status":status
                    }

            except:
                pass

    return log

df = fetch_data()

log = proses(df)

# ===================== STATISTIK =====================
total = len(MASTER)
hadir = sum(1 for n in MASTER if n in log and log[n]["status"]=="HDR")
telat = sum(1 for n in MASTER if n in log and log[n]["status"]=="TLT")
alpa = total - hadir - telat

c1,c2,c3,c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class='stat-box'>
    <div class='stat-number'>{total}</div>
    <div class='stat-label'>Total Pegawai</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class='stat-box'>
    <div class='stat-number'>{hadir}</div>
    <div class='stat-label'>Hadir</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class='stat-box'>
    <div class='stat-number'>{telat}</div>
    <div class='stat-label'>Telat</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class='stat-box'>
    <div class='stat-number'>{alpa}</div>
    <div class='stat-label'>Alpa</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ===================== HEADER TABEL =====================
h1,h2,h3,h4,h5,h6 = st.columns([1,4,2,2,2,2])

h1.markdown("**No**")
h2.markdown("**Nama**")
h3.markdown("**Masuk**")
h4.markdown("**Pulang**")
h5.markdown("**Status**")
h6.markdown("**Aksi**")

# ===================== ROW =====================
for i,nama in enumerate(MASTER,1):

    data = log.get(nama,{
    "masuk":"--",
    "pulang":"--",
    "status":"ALPA"
    })

    warna={
    "HDR":"badge-hadir",
    "TLT":"badge-telat",
    "ALPA":"badge-alpa"
    }[data["status"]]

    c1,c2,c3,c4,c5,c6 = st.columns([1,4,2,2,2,2])

    c1.write(i)
    c2.write(nama)
    c3.write(data["masuk"])
    c4.write(data["pulang"])

    c5.markdown(
    f"<span class='{warna}'>{data['status']}</span>",
    unsafe_allow_html=True
    )

    with c6:

        b1,b2 = st.columns(2)

        with b1:
            if st.button("P",key=f"p{i}"):
                kirim_absen(nama)

        with b2:
            if st.button("S",key=f"s{i}"):
                kirim_absen(nama)

# ===================== AUTO REFRESH =====================
time.sleep(10)
st.rerun()
