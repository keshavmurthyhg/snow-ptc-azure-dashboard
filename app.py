import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Operations Intelligence Dashboard")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    # 🔁 Replace with your OneDrive links later
    azure = pd.read_csv("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/All-VCE-Bugs.csv")
    ptc = pd.read_csv(
    "https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/PTC-Cases-Report.csv"
)
    snow = pd.read_excel("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/Snow-incident.xlsx")

    azure["Source"] = "Azure"
    snow["Source"] = "SNOW"
    ptc["Source"] = "PTC"

    df = pd.concat([azure, snow, ptc], ignore_index=True)

    # Clean column names
    df.columns = df.columns.str.strip()

    return df

df = load_data()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔧 Filters")

def create_filter(column):
    if column in df.columns:
        values = ["ALL"] + sorted(df[column].dropna().astype(str).unique().tolist())
        return st.sidebar.selectbox(column, values)
    return "ALL"

state = create_filter("State")
assigned = create_filter("Assigned To")
release = create_filter("Release_windchill")

# ---------------- SEARCH ----------------
keyword = st.text_input("🔍 Search (All Columns)")

filtered = df.copy()

# Apply filters
if state != "ALL":
    filtered = filtered[filtered["State"].astype(str) == state]

if assigned != "ALL":
    filtered = filtered[filtered["Assigned To"].astype(str) == assigned]

if release != "ALL":
    filtered = filtered[filtered["Release_windchill"].astype(str) == release]

# Keyword search (Excel-like)
if keyword:
    filtered = filtered[
        filtered.apply(
            lambda row: row.astype(str).str.contains(keyword, case=False).any(),
            axis=1
        )
    ]

# ---------------- OUTPUT ----------------
st.write(f"### 🔢 Results: {len(filtered)}")

st.dataframe(filtered, use_container_width=True)

st.download_button(
    "⬇️ Download Filtered Data",
    filtered.to_csv(index=False),
    "filtered_data.csv"
)
