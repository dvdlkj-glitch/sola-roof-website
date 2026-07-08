import streamlit as st

st.set_page_config(
    page_title="SOLA ROOF — Solar-Ready Roofing",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Streamlit Community Cloud's proxy breaks /app/static file serving, so the
# animated site is hosted on GitHub Pages and embedded via a main-document
# iframe (components.html would nest a fixed-height sandbox that breaks the
# scroll-driven animation).
PAGES_BASE = "https://dvdlkj-glitch.github.io/sola-roof-website"
SITE_URL = f"{PAGES_BASE}/index.html"
DASHBOARD_URL = f"{PAGES_BASE}/dashboard.html"

st.markdown(
    f"""
    <style>
      #MainMenu, header, footer {{visibility: hidden;}}
      [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {{display: none;}}
      .stApp {{background: #0e0d0c;}}
      .block-container {{padding: 0 !important; max-width: 100% !important;}}
      [data-testid="stVerticalBlock"] {{gap: 0 !important;}}
    </style>
    <iframe src="{SITE_URL}"
            style="width:100%; height:94vh; border:none; display:block; background:#0e0d0c;"
            allow="fullscreen"></iframe>
    <div style="text-align:center; padding:12px; background:#0e0d0c; color:#c8c0b4;
                font-family:sans-serif; font-size:13px;">
      Best experienced full-screen:
      <a href="{SITE_URL}" target="_blank" style="color:#f5a13d;">open the animated site</a>
      &nbsp;·&nbsp;
      <a href="{DASHBOARD_URL}" target="_blank" style="color:#f5a13d;">open the cost estimator dashboard</a>
      &nbsp;·&nbsp;
      <a href="{PAGES_BASE}/options.html" target="_blank" style="color:#f5a13d;">browse roofing options</a>
      &nbsp;·&nbsp;
      <a href="{PAGES_BASE}/salesmap.html" target="_blank" style="color:#f5a13d;">open the AI sales potential map</a>
    </div>
    """,
    unsafe_allow_html=True,
)
