import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():

    azure = pd.read_csv("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/All-VCE-Bugs.csv")
    snow = pd.read_excel("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/Snow-incident.xlsx", engine="openpyxl")
    ptc = pd.read_csv("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/PTC-Cases-Report.csv")

    # Normalize columns
    def normalize(df):
        df.columns = df.columns.str.strip().str.lower()
        return df

    azure = normalize(azure)
    snow = normalize(snow)
    ptc = normalize(ptc)

    # 🔥 AUTO COLUMN DETECTION
    def find_col(df, keywords):
        for col in df.columns:
            for key in keywords:
                if key in col:
                    return col
        return None

    def build(df, source):

        return pd.DataFrame({
            "Source": source,
            "ID": df.get(find_col(df, ["id", "number"])),
            "Title": df.get(find_col(df, ["title", "description", "name"])),
            "State": df.get(find_col(df, ["state", "status"])),
            "Assigned To": df.get(find_col(df, ["assigned", "owner"])),
            "Created Date": df.get(find_col(df, ["created", "opened"])),
            "Priority": df.get(find_col(df, ["priority", "severity"])),
            "Assignment Group": df.get(find_col(df, ["group"])),
            "Release": df.get(find_col(df, ["release"])),
            "Plant": df.get(find_col(df, ["plant"]))
        })

    azure_clean = build(azure, "Azure")
    snow_clean = build(snow, "SNOW")
    ptc_clean = build(ptc, "PTC")

    df = pd.concat([azure_clean, snow_clean, ptc_clean], ignore_index=True)

    return df


df = load_data()

# ---------------- HEADER ----------------
st.markdown("## ⚙️ Ops Insight Dashboard")

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## ⚙️ Ops Insight Dashboard")
st.sidebar.markdown("### 🔧 Filters")

source = st.sidebar.selectbox("Source", ["ALL", "Azure", "SNOW", "PTC"])

filtered = df.copy()

if source != "ALL":
    filtered = filtered[filtered["Source"] == source]

# ---------------- FILTER FUNCTION ----------------
def create_filter(data, column):
    if column in data.columns:
        vals = data[column].dropna().astype(str).unique().tolist()
        if len(vals) == 0:
            return "ALL"
        return st.sidebar.selectbox(column, ["ALL"] + sorted(vals))
    return "ALL"

# ---------------- FILTERS ----------------
state = create_filter(filtered, "State")

if state != "ALL":
    filtered = filtered[filtered["State"].astype(str) == state]

if source == "Azure":
    assigned = create_filter(filtered, "Assigned To")
    release = create_filter(filtered, "Release")

    if assigned != "ALL":
        filtered = filtered[filtered["Assigned To"].astype(str) == assigned]

    if release != "ALL":
        filtered = filtered[filtered["Release"].astype(str) == release]

elif source == "SNOW":
    priority = create_filter(filtered, "Priority")
    group = create_filter(filtered, "Assignment Group")

    if priority != "ALL":
        filtered = filtered[filtered["Priority"].astype(str) == priority]

    if group != "ALL":
        filtered = filtered[filtered["Assignment Group"].astype(str) == group]

elif source == "PTC":
    owner = create_filter(filtered, "Assigned To")
    plant = create_filter(filtered, "Plant")

    if owner != "ALL":
        filtered = filtered[filtered["Assigned To"].astype(str) == owner]

    if plant != "ALL":
        filtered = filtered[filtered["Plant"].astype(str) == plant]

# ---------------- KPI (LEFT SIDEBAR STYLE) ----------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 KPI")

total = len(filtered)
open_count = filtered["State"].astype(str).str.contains("open|new", case=False, na=False).sum()
closed_count = filtered["State"].astype(str).str.contains("closed|resolved", case=False, na=False).sum()

st.sidebar.markdown(f"**Total:** {total}")
st.sidebar.markdown(f"**Open:** {open_count}")
st.sidebar.markdown(f"**Closed:** {closed_count}")

# ---------------- SEARCH ----------------
keyword = st.text_input("🔍 Search")

if keyword:
    filtered = filtered[
        filtered.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)
    ]

# ---------------- TABLE ----------------
st.write(f"### 🔢 Results: {len(filtered)}")

cols = [
    "Source", "ID", "Title", "State", "Assigned To",
    "Priority", "Assignment Group", "Release", "Plant", "Created Date"
]

cols = [c for c in cols if c in filtered.columns]

st.dataframe(filtered[cols], use_container_width=True)

# ---------------- DOWNLOAD ----------------
st.download_button(
    "⬇️ Download",
    filtered.to_csv(index=False),
    "filtered.csv"
)
