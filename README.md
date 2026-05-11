[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=Momahmoses%2Fng-conflict-analysis&branch=main&mainModule=app.py)

# ⚠ Nigeria Conflict & Security Incident Analyzer

Geospatial conflict intelligence platform tracking insurgency, banditry, farmer-herder clashes, and communal violence across Nigeria using **ACLED-style data**, **PySpark**, **GIS KDE analysis**, **Azure Cognitive Search**, and **Streamlit**.

## Problem Statement
Nigeria faces multi-dimensional security crises — Boko Haram/ISWAP in the NE, armed banditry in the NW, farmer-herder conflicts in the NC, and unknown gunmen in the SE. These displace millions and reduce agricultural output by up to 65% in affected areas. This platform helps the NSA, military, and development agencies understand conflict patterns.

## Quick Start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data Sources (Production)
- **ACLED** — Armed Conflict Location & Event Data Project
- **UNHCR** — Displacement tracking
- **ISWAP/Boko Haram tracker** — CSIS, Africa Center for Strategic Studies
- **Nigeria Police Force** — Crime statistics
