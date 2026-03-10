import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from io import StringIO
import time

st.set_page_config(layout="wide")

# ================= STYLE =================
st.markdown("""
<style>

html, body, [class*="css"]{
font-size:16px;
}

.title{
text-align:center;
font-size:30px;
font-weight:bold;
}

.clock{
text-align:center;
font-size:42px;
color:#3fa7ff;
margin-bottom:10px;
}

.card{
background:#111;
padding:15px;
border-radius:10px;
border:1px solid #333;
text-align:center;
}

.card h2{
margin:0;
}

.status-hadir{color:#2ecc71;font-weight:bold;}
.status-telat{color:#f1c40f;font-weight:bold;}
.status-alpa{color:#e74c3c;font-weight:bold;}

.stButton button{
border-radius:50%;
height:40px;
width:40px;
}

@media (max-width:640px){

.title{font-size:22px;}
.clock{font-size:32px;}

}

</style>
""", unsafe_allow_html=True)

# ================= MASTER =================
MASTER = [
"Suwanto","Wawan Setiawan","Ineke Setiyaningsih",
"Farah Agustina Setiawati","Rusma Ariati",
"Sya'bani Rona Baika","Apriadi Rakhman",
"M Satria Maipadly","Basuki Rahmat",
"Sulaiman","Saldoz Yedi","Mastoni Ridani",
"Suriadi","Ami Aspihani","Abdurrahman",
"Emaliani","Muhammad Hafiz Rijani",
"Saiful Fahmi","Nadianti"
]

# ================= URL =================
CSV_URL = "ISI_URL_CSV_GOOGLE_SHEET"
FORM_URL = "ISI_URL_FORM"
ENTRY_ID = "entry.960346359"

# ================= HEADER =================
now = datetime.now()

st.markdown("<div class='title'>MONITORING ABSENSI KPU HSS</div>",unsafe_allow_html=True)

st.markdown(
f"<div class='clock'>{now.strftime('%H:%M:%S')}</div>",
unsafe_allow_html=True
)

tanggal = st.date_input("Tanggal", now.date())

if st.button("🔍 Cek Absensi"):
    st.rerun()

# ================= FETCH =================
def fetch():

    try:

        r = requests.get(CSV_URL)

        df = pd.read_csv(StringIO(r.text))

        df.columns = df.columns.str.strip()

        return df

    except:

        return pd.DataFrame()

# ================= KIRIM ABSEN =================
def kirim(nama):

    payload={ENTRY_ID:nama}

    requests.post(FORM_URL,data=payload)

    st.success("Absensi terkirim")

    time.sleep(1)

    st.rerun()

# ================= PROSES =================
def proses(df):

    log={}

    if df.empty:
        return log

    waktu_col=df.columns[0]

    # cari kolom nama otomatis
    nama_col=None
    for c in df.columns:
        if "nama" in c.lower():
            nama_col=c

    if nama_col is None:
        nama_col=df.columns[1]

    for _,r in df.iterrows():

        ts=pd.to_datetime(r[waktu_col],errors="coerce")

        if pd.isna(ts):
            continue

        nama=str(r[nama_col]).strip()

        if ts.date()==tanggal:

            jam=ts.strftime("%H:%M")

            status="HDR" if ts.hour<9 else "TLT"

            log[nama]={
            "masuk":jam,
            "status":status
            }

    return log

df=fetch()

log=proses(df)

# ================= STAT =================
total=len(MASTER)

hadir=sum(1 for n in MASTER if n in log)

telat=sum(1 for n in MASTER if n in log and log[n]["status"]=="TLT")

alpa=total-hadir

c1,c2,c3,c4=st.columns(4)

c1.markdown(f"<div class='card'><h2>{total}</h2>Total Pegawai</div>",unsafe_allow_html=True)
c2.markdown(f"<div class='card'><h2>{hadir}</h2>Hadir</div>",unsafe_allow_html=True)
c3.markdown(f"<div class='card'><h2>{telat}</h2>Telat</div>",unsafe_allow_html=True)
c4.markdown(f"<div class='card'><h2>{alpa}</h2>Alpa</div>",unsafe_allow_html=True)

st.divider()

# ================= HEADER =================
h1,h2,h3,h4,h5=st.columns([1,4,2,2,2])

h1.write("No")
h2.write("Nama")
h3.write("Masuk")
h4.write("Status")
h5.write("Aksi")

# ================= ROW =================
for i,nama in enumerate(MASTER,1):

    data=log.get(nama,{"masuk":"--","status":"ALPA"})

    warna={
    "HDR":"status-hadir",
    "TLT":"status-telat",
    "ALPA":"status-alpa"
    }[data["status"]]

    c1,c2,c3,c4,c5=st.columns([1,4,2,2,2])

    c1.write(i)
    c2.write(nama)
    c3.write(data["masuk"])

    c4.markdown(
    f"<span class='{warna}'>{data['status']}</span>",
    unsafe_allow_html=True
    )

    with c5:

        b1,b2=st.columns(2)

        with b1:
            if st.button("P",key=f"p{i}"):
                kirim(nama)

        with b2:
            if st.button("S",key=f"s{i}"):
                kirim(nama)

# ================= DEBUG =================
with st.expander("DEBUG DATA GOOGLE SHEET"):
    st.dataframe(df)
