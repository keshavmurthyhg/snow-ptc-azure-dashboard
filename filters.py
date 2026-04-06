import streamlit as st

def create_filter(data, col):
    vals = data[col].dropna().astype(str).unique().tolist()
    return st.sidebar.selectbox(col, ["ALL"] + sorted(vals)) if vals else "ALL"

def apply_filters(df, state, priority, release, keyword):

    filtered = df.copy()

    if state != "ALL":
        filtered = filtered[filtered["Status"] == state]

    if priority != "ALL":
        filtered = filtered[filtered["Priority"] == priority]

    if release != "ALL":
        filtered = filtered[filtered["Release"] == release]

    if keyword:
        filtered = filtered[
            filtered.apply(lambda r: r.astype(str).str.contains(keyword, case=False).any(), axis=1)
        ]

    return filtered.reset_index(drop=True)
