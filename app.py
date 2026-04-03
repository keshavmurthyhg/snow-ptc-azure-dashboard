import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():

    azure = pd.read_csv("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/All-VCE-Bugs.csv")
    snow = pd.read_excel("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/Snow-incident.xlsx", engine="openpyxl")
    ptc = pd.read_csv("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/PTC-Cases-Report.csv")

    def norm(df):
        df.columns = df.columns.str.strip().str.lower()
        return df

    azure, snow, ptc = norm(azure), norm(snow), norm(ptc)

    def build_azure(df):
        return pd.DataFrame({
            "ID": df.get("id"),
            "Title": df.get("title"),
            "State": df.get("state"),
            "Created By": df.get("created by"),
            "Created Date": df.get("created date"),
            "Assigned To": df.get("assigned to"),
            "Resolved Date": df.get("resolved date"),
            "Release": df.get("release_windchill"),
            "Priority": None,
            "Source": "Azure"
        })

    def build_snow(df):
        return pd.DataFrame({
            "ID": df.get("number"),
            "Title": df.get("short description"),
            "State": df.get("incident state"),
            "Created By": None,
            "Created Date": df.get("created"),
            "Assigned To": df.get("assigned to"),
            "Resolved Date": df.get("resolved"),
            "Release": None,
            "Priority": df.get("priority"),
            "Source": "SNOW"
        })

    def build_ptc(df):
        return pd.DataFrame({
            "ID": df.get("case number"),
            "Title": df.get("subject"),
            "State": df.get("status"),
            "Created By": df.get("case contact"),
            "Created Date": df.get("created date"),
            "Assigned To": df.get("case assignee"),
            "Resolved Date": df.get("resolved date"),
            "Release": None,
            "Priority": df.get("severity"),
            "Source": "PTC"
        })

    df = pd.concat([
        build_azure(azure),
        build_snow(snow),
        build_ptc(ptc)
    ], ignore_index=True)

    return df


df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## ⚙️ Ops Insight Dashboard")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox("Menu", ["Search Tool"])

st.sidebar.markdown("### 🔧 Filters")

# ---------------- FILTER FUNCTION ----------------
def create_filter(data, column):
    vals = data[column].dropna().astype(str).unique().tolist()
    if len(vals) == 0:
        return "ALL"
    return st.sidebar.selectbox(column, ["ALL"] + sorted(vals))

# ---------------- SEARCH ----------------
keyword = st.text_input("🔍 Search")

# ---------------- KPI FUNCTION ----------------
def show_kpi(data):
    total = len(data)
    open_count = data["State"].astype(str).str.contains("open|new", case=False, na=False).sum()
    closed_count = data["State"].astype(str).str.contains("closed|resolved", case=False, na=False).sum()
    cancelled_count = data["State"].astype(str).str.contains("cancel", case=False, na=False).sum()

    col1, col2 = st.sidebar.columns(2)
    col1.metric("Total", total)
    col2.metric("Open", open_count)

    col3, col4 = st.sidebar.columns(2)
    col3.metric("Closed", closed_count)
    col4.metric("Cancelled", cancelled_count)

# ---------------- COMMON TABLE FUNCTION ----------------
def render(data):

    filtered = data.copy()

    # Filters
    state = create_filter(filtered, "State")
    if state != "ALL":
        filtered = filtered[filtered["State"] == state]

    if "Release" in filtered.columns:
        if filtered["Release"].notna().any():
            release = create_filter(filtered, "Release")
            if release != "ALL":
                filtered = filtered[filtered["Release"] == release]

    if "Priority" in filtered.columns:
        if filtered["Priority"].notna().any():
            priority = create_filter(filtered, "Priority")
            if priority != "ALL":
                filtered = filtered[filtered["Priority"] == priority]

    # Search
    if keyword:
        filtered = filtered[
            filtered.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)
        ]

    # KPI
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 KPI")
    show_kpi(filtered)

    # Reset index
    filtered = filtered.reset_index(drop=True)
    filtered.index += 1

    st.write(f"### 🔢 Results: {len(filtered)}")

    cols = [
        "Source","ID","Title","Release","State",
        "Created By","Created Date","Assigned To","Resolved Date","Priority"
    ]
    cols = [c for c in cols if c in filtered.columns]

    st.dataframe(filtered[cols], use_container_width=True)

    st.download_button(
        "⬇️ Download",
        filtered.to_csv(index=False),
        "filtered_data.csv"
    )

# ---------------- TABS ----------------
tab_all, tab_az, tab_snow, tab_ptc = st.tabs(["All", "Azure", "SNOW", "PTC"])

with tab_all:
    render(df)

with tab_az:
    render(df[df["Source"] == "Azure"])

with tab_snow:
    render(df[df["Source"] == "SNOW"])

with tab_ptc:
    render(df[df["Source"] == "PTC"])
