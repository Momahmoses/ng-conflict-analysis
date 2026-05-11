"""Nigeria Conflict & Security Incident Analyzer — Streamlit Dashboard"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from data.generate_data import generate_conflict_incidents, generate_state_security_index, INCIDENT_TYPES
from gis.spatial_analysis import build_conflict_map

st.set_page_config(page_title="NG Conflict Analysis", page_icon="⚠", layout="wide")
st.markdown("""<style>
.kpi{background:#37474f;color:white;padding:14px;border-radius:8px;text-align:center;border-left:4px solid #ff5722;}
.kpi-val{font-size:1.9rem;font-weight:700;}
.kpi-lbl{font-size:.8rem;opacity:.8;}
</style>""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    incidents = generate_conflict_incidents(1500)
    security = generate_state_security_index()
    incidents["date"] = pd.to_datetime(incidents["date"])
    return incidents, security


def main():
    incidents_df, security_df = load_data()

    with st.sidebar:
        st.title("⚠ Conflict Analysis")
        st.caption("Nigeria Security Intelligence")
        st.divider()
        conflict_types = st.multiselect("Conflict Type",
                                         incidents_df["conflict_type"].unique().tolist(),
                                         default=incidents_df["conflict_type"].unique().tolist()[:4])
        event_types = st.multiselect("Event Type", INCIDENT_TYPES, default=INCIDENT_TYPES[:4])
        year_filter = st.slider("Year", 2020, 2023, (2021, 2023))
        severity = st.multiselect("Severity", ["Low", "Medium", "High"],
                                   default=["Medium", "High"])
        st.divider()
        st.markdown("**Data Source**")
        st.info("ACLED-style incident records")
        st.info("Azure Cognitive Search NLP")

    filtered = incidents_df[
        incidents_df["conflict_type"].isin(conflict_types) &
        incidents_df["event_type"].isin(event_types) &
        incidents_df["date"].dt.year.between(year_filter[0], year_filter[1]) &
        incidents_df["severity"].isin(severity)
    ]

    st.title("⚠ Nigeria Conflict & Security Incident Analyzer")
    st.caption("Incident mapping · Hotspot detection · Actor networks · GIS + PySpark + Azure Cognitive")
    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    total_inc = len(filtered)
    total_fat = filtered["fatalities"].sum()
    total_disp = filtered["displaced"].sum()
    hot_states = filtered.groupby("state")["fatalities"].sum().nlargest(3).index.tolist()
    for col, val, lbl in zip(
        [c1, c2, c3, c4],
        [total_inc, f"{total_fat:,}", f"{total_disp:,}", ", ".join(hot_states[:2])],
        ["Total Incidents", "Total Fatalities", "Total Displaced", "Top Hotspot States"]
    ):
        col.markdown(f'<div class="kpi"><div class="kpi-val">{val}</div>'
                     f'<div class="kpi-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.divider()
    col_map, col_chart = st.columns([3, 2])

    with col_map:
        st.subheader("🗺 Conflict Hotspot Map")
        m = build_conflict_map(filtered, security_df)
        st_folium(m, width=700, height=460)

    with col_chart:
        st.subheader("📊 Fatalities by State")
        state_fat = filtered.groupby("state")["fatalities"].sum().sort_values().tail(15).reset_index()
        fig = px.bar(state_fat, x="fatalities", y="state", orientation="h",
                     color="fatalities", color_continuous_scale="Reds",
                     labels={"fatalities": "Total Fatalities", "state": ""}, height=460)
        fig.update_layout(coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=0, r=10, t=5, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    col_timeline, col_event = st.columns(2)

    with col_timeline:
        st.subheader("📈 Incident Timeline")
        monthly = (filtered.set_index("date").resample("ME")
                   .agg(incidents=("event_id", "count"),
                        fatalities=("fatalities", "sum"))
                   .reset_index())
        fig_t = px.line(monthly, x="date", y=["incidents", "fatalities"],
                        labels={"value": "Count", "date": ""},
                        color_discrete_sequence=["#ff5722", "#b71c1c"])
        fig_t.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=0, r=0, t=5, b=0))
        st.plotly_chart(fig_t, use_container_width=True)

    with col_event:
        st.subheader("🔫 Incident Type Breakdown")
        evt = filtered["event_type"].value_counts().reset_index()
        evt.columns = ["type", "count"]
        fig_e = px.pie(evt, names="type", values="count", hole=0.4,
                       color_discrete_sequence=px.colors.qualitative.Set1)
        fig_e.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_e, use_container_width=True)

    st.divider()
    st.subheader("📋 Security Index by State")
    st.dataframe(
        security_df[["state", "conflict_type", "incidents_2023", "fatalities_2023",
                      "displaced_2023", "security_index", "ag_impact_pct"]]
        .sort_values("security_index", ascending=False)
        .style.background_gradient(subset=["security_index"], cmap="RdYlGn_r"),
        use_container_width=True, height=300,
    )
    st.caption("Data: Synthetic — replace with ACLED Nigeria, ISWAP/Boko Haram tracker, "
               "UNHCR displacement data. Pipeline: Azure Databricks + Azure Cognitive Search.")


if __name__ == "__main__":
    main()
