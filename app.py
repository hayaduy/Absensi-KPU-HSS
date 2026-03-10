import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from io import StringIO
import random

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# ================= CSS =================
st.markdown("""
<style>

.title{
text-align:center;
font-size:28px;
font-weight:bold;
}

.clock{
text-align:center;
font-size:48px;
color:#3498db;
margin-bottom:20px;
}

table{
width:100%;
border-collapse:collapse;
}

th{
text-align:left;
padding:10px;
border-bottom:2px solid #444;
}

td{
padding:10px;
border-bottom:1px solid #333;
}

.status-hadir{
color:#2ecc71;
font-weight:bold;
}

.status-telat{
color:#f39c12;
font-weight:bold;
}

.status-alpa{
color:#e74c3c;
font-weight:bold;
}

button[kind="primary"]{
border-radius:50%;
width:45px;
height:45px;
font-weight:bold;
}

@media (max-width:768px){

th:nth-child(1),
td:nth-child(1){
display:none;
}

.clock{
font-size:36px;
}

}

</style>
""", unsafe_allow_html=True)

# ================= MASTER DATA =================
MASTER_DATA = {
"PNS":[
"Suwanto",
"Wawan Setiawan",
"Ineke Setiyaningsih",
"Farah Agustina Setiawati",
"Rusma Ariati"
],

"PPPK":[
"Sya'bani Rona Baika",
"Apriadi Rakhman",
"M Satria Maipadly",
"Basuki Rahmat",
"Sulaiman",
"Saldoz Yedi",
"Mastoni Ridani",
"Suriadi",
"Ami Aspihani",
"Abdurrahman"
]
}

# ================= URL =================
URL_PNS = "URL_CSV_PNS"
URL_PPPK = "URL_CSV_PPPK"

FORM_PNS = "URL_FORM_PNS"
FORM_PPPK = "URL_FORM_PPPK"

ENTRY_ID = "entry.960346359"

# ================= TIME =================
wita_now = datetime.now() + timedelta(hours=8)

# ================= HEADER =================
st.markdown("<div class='title'>MONITORING ABSENSI KPU HSS</div>", unsafe_allow_html=True)

st.markdown(
f"<div class='clock'>{wita_now.strftime('%H:%M:%S')}</div>",
unsafe_allow_html=True
)

tanggal = st.date_input("Tanggal", wita_now.date())

# ================= FETCH DATA =================
def fetch_data(url):

    try:

        r = requests.get(f"{url}&cache={random.random()}", timeout=10)

        df = pd.read_csv(StringIO(r.text))

        return df

    except:

        return pd.DataFrame()

# ================= KIRIM DATA =================
def kirim_absen(url,nama):

    payload = {
        ENTRY_ID: nama
    }

    headers = {
        "User-Agent":"Mozilla/5.0",
        "Content-Type":"application/x-www-form-urlencoded"
    }

    try:

        r = requests.post(url,data=payload,headers=headers)

        if r.status_code == 200:

            st.success("Absensi berhasil")

            st.rerun()

        else:

            st.error("Gagal kirim ke Google Form")

    except Exception as e:

        st.error(e)

# ================= PROSES LOG =================
def proses_log(df):

    log = {}

    batas_masuk = datetime.strptime("09:00","%H:%M").time()
    batas_pulang = datetime.strptime("16:00","%H:%M").time()

    if not df.empty:

        for _,r in df.iterrows():

            try:

                ts = pd.to_datetime(r.iloc[0],dayfirst=True)

                nama = str(r.iloc[1]).strip()

                if ts.date() == tanggal:

                    jam = ts.time()

                    if nama not in log:

                        status = "HDR" if jam <= batas_masuk else "TLT"

                        log[nama] = {
                        "m":jam.strftime("%H:%M"),
                        "p":"--",
                        "k":status
                        }

                    elif jam >= batas_pulang:

                        log[nama]["p"] = jam.strftime("%H:%M")

            except:
                pass

    return log

# ================= RENDER TABLE =================
def render(master,log,form_url,prefix):

    header_html = """
<table>
<tr>
<th>No</th>
<th>Nama</th>
<th>Pagi</th>
<th>Sore</th>
<th>Status</th>
<th>Aksi</th>
</tr>
"""

    st.markdown(header_html,unsafe_allow_html=True)

    for i,nama in enumerate(master,1):

        data = log.get(nama,{
        "m":"--",
        "p":"--",
        "k":"ALPA"
        })

        status_class = {
        "HDR":"status-hadir",
        "TLT":"status-telat",
        "ALPA":"status-alpa"
        }[data["k"]]

        row_html = f"""
<tr>
<td>{i}</td>
<td>{nama}</td>
<td>{data['m']}</td>
<td>{data['p']}</td>
<td class="{status_class}">{data['k']}</td>
<td></td>
</tr>
"""

        st.markdown(row_html,unsafe_allow_html=True)

        c1,c2 = st.columns(2)

        with c1:
            if st.button("P",key=f"p_{prefix}_{i}"):
                kirim_absen(form_url,nama)

        with c2:
            if st.button("S",key=f"s_{prefix}_{i}"):
                kirim_absen(form_url,nama)

    st.markdown("</table>",unsafe_allow_html=True)

# ================= TAB =================
tab1,tab2 = st.tabs(["PNS","PPPK"])

with tab1:

    df = fetch_data(URL_PNS)

    log = proses_log(df)

    render(MASTER_DATA["PNS"],log,FORM_PNS,"pns")

with tab2:

    df = fetch_data(URL_PPPK)

    log = proses_log(df)

    render(MASTER_DATA["PPPK"],log,FORM_PPPK,"pppk")
