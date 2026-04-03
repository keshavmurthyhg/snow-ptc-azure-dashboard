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

    return pd.concat([
        build_azure(azure),
        build_snow(snow),
        build_ptc(ptc)
    ], ignore_index=True)


df = load_data()

# ---------------- SIDEBAR (ONLY ONCE) ----------------
st.sidebar.markdown("## ⚙️ Ops Insight Dashboard")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox("Menu", ["Search Tool"])

st.sidebar.markdown("### 🔧 Filters")

# FILTERS CREATED ONLY ONCE
def create_filter(data, column):
    vals = data[column].dropna().astype(str).unique().tolist()
    if len(vals) == 0:
        return "ALL"
    return st.sidebar.selectbox(column, ["ALL"] + sorted(vals))

state_filter = create_filter(df, "State")

release_filter = "ALL"
if df["Release"].notna().any():
    release_filter = create_filter(df, "Release")

priority_filter = "ALL"
if df["Priority"].notna().any():
    priority_filter = create_filter(df, "Priority")

# ---------------- SEARCH ----------------
keyword = st.text_input("🔍 Search")

# ---------------- KPI (BASED ON FULL DATA ONLY) ----------------
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

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 KPI")
show_kpi(df)  # ALWAYS FULL DATA

# ---------------- MAIN FILTER FUNCTION ----------------
def apply_filters(data):

    filtered = data.copy()

    if state_filter != "ALL":
        filtered = filtered[filtered["State"] == state_filter]

    if release_filter != "ALL":
        filtered = filtered[filtered["Release"] == release_filter]

    if priority_filter != "ALL":
        filtered = filtered[filtered["Priority"] == priority_filter]

    if keyword:
        filtered = filtered[
            filtered.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)
        ]

    return filtered.reset_index(drop=True)


# ---------------- TABS ----------------
tab_all, tab_az, tab_snow, tab_ptc = st.tabs(["All", "Azure", "SNOW", "PTC"])

def show_table(data):
    data = apply_filters(data)
    data.index += 1

    st.write(f"### 🔢 Results: {len(data)}")

    cols = [
        "Source","ID","Title","Release","State",
        "Created By","Created Date","Assigned To","Resolved Date","Priority"
    ]
    cols = [c for c in cols if c in data.columns]

    st.dataframe(data[cols], use_container_width=True)

    st.download_button(
        "⬇️ Download",
        data.to_csv(index=False),
        "filtered_data.csv"
    )


with tab_all:
    show_table(df)

with tab_az:
    show_table(df[df["Source"] == "Azure"])

with tab_snow:
    show_table(df[df["Source"] == "SNOW"])

with tab_ptc:
    show_table(df[df["Source"] == "PTC"])
