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

    return pd.concat([build_azure(azure), build_snow(snow), build_ptc(ptc)], ignore_index=True)


df = load_data()

# ---------------- SESSION STATE ----------------
if "search" not in st.session_state:
    st.session_state.search = ""

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## ⚙️ Ops Insight Dashboard")

menu = st.sidebar.selectbox("Menu", ["Search Tool"])

st.sidebar.markdown("---")

# ---------------- FILTERS ----------------
st.sidebar.markdown("### 🔧 Filters")

# (empty initially — will populate after search)

# ---------------- KPI (ALWAYS BASED ON FULL DATA) ----------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 KPI")

def get_kpi(data):
    total = len(data)
    open_count = data["State"].astype(str).str.contains("open|new", case=False, na=False).sum()
    closed = data["State"].astype(str).str.contains("closed|resolved", case=False, na=False).sum()
    cancelled = data["State"].astype(str).str.contains("cancel", case=False, na=False).sum()
    return total, open_count, closed, cancelled

# ---------------- SEARCH ----------------
st.markdown("### 🔍 Search")

col1, col2 = st.columns([10,1])

search_input = col1.text_input(
    "",
    value=st.session_state.search,
    placeholder="Type keyword and press Enter"
)

if col2.button("❌"):
    st.session_state.search = ""
    st.rerun()

st.session_state.search = search_input
keyword = st.session_state.search

# ---------------- TABS ----------------
tab_all, tab_az, tab_snow, tab_ptc = st.tabs(["All", "Azure", "SNOW", "PTC"])

def render(tab_name):

    # KPI BASED ON TAB (NOT SEARCH)
    if tab_name == "All":
        base = df
    else:
        base = df[df["Source"] == tab_name]

    t,o,c,x = get_kpi(base)

    colA, colB = st.sidebar.columns(2)
    colA.markdown(f"**Total**  \n{t}")
    colB.markdown(f"**Open**  \n{o}")

    colC, colD = st.sidebar.columns(2)
    colC.markdown(f"**Closed**  \n{c}")
    colD.markdown(f"**Cancelled**  \n{x}")

    # NO SEARCH → STOP
    if not keyword:
        st.info("🔍 Enter a keyword to begin search")
        return

    # SEARCH FIRST
    searched = df[
        df.apply(lambda r: r.astype(str).str.contains(keyword, case=False).any(), axis=1)
    ]

    # THEN TAB FILTER
    if tab_name != "All":
        searched = searched[searched["Source"] == tab_name]

    # FILTERS AFTER SEARCH
    st.sidebar.markdown("### 🔧 Filters")

    state = st.sidebar.selectbox("State", ["ALL"] + sorted(searched["State"].dropna().unique()))

    if state != "ALL":
        searched = searched[searched["State"] == state]

    # TABLE
    searched = searched.reset_index(drop=True)
    searched.index += 1

    st.markdown(f"#### Results: {len(searched)}")

    cols = [
        "Source",
        "ID",
        "Title",
        "Release",
        "State",
        "Created By",
        "Created Date",
        "Assigned To",
        "Resolved Date",
        "Priority"
    ]

    cols = [c for c in cols if c in searched.columns]

    st.dataframe(searched[cols], use_container_width=True, height=450)

    st.download_button(
        "⬇️ Download",
        searched.to_csv(index=False),
        f"{tab_name}_data.csv"
    )


with tab_all:
    render("All")

with tab_az:
    render("Azure")

with tab_snow:
    render("SNOW")

with tab_ptc:
    render("PTC")
