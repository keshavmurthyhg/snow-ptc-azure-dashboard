import streamlit as st

def show_kpi(data):

    total = len(data)
    open_count = data["Status"].astype(str).str.contains("open|new", case=False, na=False).sum()
    closed_count = data["Status"].astype(str).str.contains("closed|resolved", case=False, na=False).sum()
    cancelled = data["Status"].astype(str).str.contains("cancel", case=False, na=False).sum()

    c1, c2 = st.sidebar.columns(2)
    c1.metric("Total", total)
    c2.metric("Open", open_count)

    c3, c4 = st.sidebar.columns(2)
    c3.metric("Closed", closed_count)
    c4.metric("Cancelled", cancelled)
