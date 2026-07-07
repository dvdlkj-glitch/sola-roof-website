from urllib.parse import quote

import pandas as pd
import streamlit as st

st.set_page_config(page_title="SOLA ROOF", page_icon="🏠", layout="wide")

# Streamlit Community Cloud's proxy breaks /app/static file serving, so the
# animated site is hosted on GitHub Pages and embedded via a main-document
# iframe (components.html would nest a fixed-height sandbox that breaks the
# scroll-driven animation).
PAGES_BASE = "https://dvdlkj-glitch.github.io/sola-roof-website"
SITE_URL = f"{PAGES_BASE}/index.html"
DASHBOARD_URL = f"{PAGES_BASE}/dashboard.html"

# ---------------- Catalog data (from roofing_products_sample.csv) ----------------
PRODUCTS = {
    "MR-750": dict(name="Longrun Metal Roofing 750", cat="Metal Roofing", low=55, high=95,
                   heat="2/5", noise="2/5", dur="Medium-High",
                   pitch="Cost-effective long-span metal roof with flexible colour and profile selection.",
                   best="Terrace house, shoplot, warehouse"),
    "CL-680": dict(name="Clip Lock Roofing System", cat="Premium Metal Roofing", low=85, high=145,
                   heat="2/5", noise="2/5", dur="High",
                   pitch="Concealed-fixing roofing system for cleaner appearance and better water resistance.",
                   best="Low slope roof, commercial, modern bungalow"),
    "PU-50": dict(name="PU Insulated Metal Roof Panel", cat="Heat Insulation Upgrade", low=120, high=220,
                  heat="5/5", noise="4/5", dur="High",
                  pitch="Metal roof with PU insulation core to reduce heat transfer and improve indoor comfort.",
                  best="Factory, office, school, café, container building"),
    "ST-ROOF": dict(name="Stone Coated Metal Roof Tile", cat="Aesthetic Roof Upgrade", low=110, high=200,
                    heat="3/5", noise="3/5", dur="High",
                    pitch="Premium roof tile appearance with metal roof weight advantage.",
                    best="Bungalow, homestay, resort, premium residential"),
    "LGS-TRUSS": dict(name="Lightweight Steel Roof Truss", cat="Roof Structure", low=65, high=130,
                      heat="N/A", noise="N/A", dur="High",
                      pitch="Engineered lightweight steel truss for predictable structural performance.",
                      best="New build, renovation, modular, IBS project"),
    "INS-FOIL": dict(name="Heat & Sound Insulation Layer", cat="Heat Insulation Upgrade", low=18, high=45,
                     heat="3/5", noise="3/5", dur="Medium",
                     pitch="Add-on insulation layer to improve comfort without full roof system change.",
                     best="Residential, shoplot, container café, site office"),
    "WPG-01": dict(name="Waterproofing & Gutter Package", cat="Roof Repair Solution", low=1500, high=15000,
                   heat="N/A", noise="N/A", dur="Medium", per_job=True,
                   pitch="Roof leak repair covering sealant, flashing, gutter and drainage improvement.",
                   best="Old house, shoplot, factory, school"),
    "CAN-01": dict(name="Canopy / Awning Roof Package", cat="Commercial Add-On", low=90, high=180,
                   heat="3/5", noise="2/5", dur="Medium-High",
                   pitch="Practical add-on canopy for retail frontage and outdoor seating comfort.",
                   best="Container café, shop entrance, car porch"),
}

SOLAR_RATE = (2800, 3800)     # RM per kWp installed
BATTERY = (12000, 18000)      # 10 kWh sample
GUTTER_PCT = (0.06, 0.10)     # of roofing material value
LABOR_PCT = (0.12, 0.18)      # of roof scope
PEAK_SUN, PERF, TARIFF = 4.5, 0.8, 0.34  # Sabah sample solar assumptions

rm = lambda v: f"RM {v:,.0f}"


# ================================================================
# Page 1 — Animated showcase (GitHub Pages embed)
# ================================================================
def showcase():
    st.markdown(
        f"""
        <style>
          #MainMenu, footer {{visibility: hidden;}}
          .stApp {{background: #0e0d0c;}}
          .block-container {{padding: 0 !important; max-width: 100% !important;}}
          [data-testid="stVerticalBlock"] {{gap: 0 !important;}}
          [data-testid="stHeader"] {{background: rgba(14,13,12,0.6);}}
        </style>
        <iframe src="{SITE_URL}"
                style="width:100%; height:92vh; border:none; display:block; background:#0e0d0c;"
                allow="fullscreen"></iframe>
        <div style="text-align:center; padding:12px; background:#0e0d0c; color:#c8c0b4;
                    font-family:sans-serif; font-size:13px;">
          Best experienced full-screen:
          <a href="{SITE_URL}" target="_blank" style="color:#f5a13d;">open the animated site</a>
          &nbsp;·&nbsp;
          <a href="{DASHBOARD_URL}" target="_blank" style="color:#f5a13d;">open the HTML cost dashboard</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ================================================================
# Page 2 — Cost estimator with material breakdown
# ================================================================
def estimator():
    st.title("🏠 SOLA ROOF — Material Breakdown & Cost Estimator")
    st.caption("Solar-ready roofing systems · Kota Kinabalu, Sabah — sample estimate ranges only, not a formal quotation.")

    # ---------------- Sidebar config ----------------
    with st.sidebar:
        st.header("Configure your estimate")
        building = st.selectbox("Building Type", [
            "Terrace House", "Bungalow / Semi-D", "Shoplot / Commercial",
            "Factory / Warehouse", "Container Café / Modular", "Resort / Homestay"], index=1)
        area = st.number_input("Roof Area (sqm)", min_value=10, max_value=20000, value=120)
        st.caption("Tip: floor area × 1.1–1.3 is a rough roof-area guide for pitched roofs.")
        sys_id = st.selectbox(
            "Roofing System", ["MR-750", "CL-680", "PU-50", "ST-ROOF"], index=2,
            format_func=lambda k: f"{PRODUCTS[k]['name']} — RM {PRODUCTS[k]['low']}–{PRODUCTS[k]['high']}/sqm")
        st.subheader("Structure & Add-Ons")
        has_truss = st.checkbox("Lightweight steel roof truss", value=True)
        has_insul = st.checkbox("Extra foil insulation layer")
        has_gutter = st.checkbox("Gutter, flashing & ridge", value=True)
        has_wp = st.checkbox("Waterproofing repair package")
        st.subheader("Solar Package")
        kwp = st.selectbox("Solar PV size", [0, 4, 6, 10, 20], index=1,
                           format_func=lambda k: "No solar (roof only)" if k == 0 else f"{k} kWp")
        has_batt = st.checkbox("Add battery storage (10 kWh)")
        carport = st.number_input("Solar Carport (sqm, 0 = none)", min_value=0, max_value=500, value=0)

    # ---------------- Breakdown calculation ----------------
    sys = PRODUCTS[sys_id]
    rows = []

    def add(name, basis, low, high, group):
        rows.append(dict(Item=name, Basis=basis, Low=low, High=high, Group=group))

    add(sys["name"], f"{area} sqm × RM {sys['low']}–{sys['high']}", area * sys["low"], area * sys["high"], "Roofing")
    if has_truss:
        t = PRODUCTS["LGS-TRUSS"]
        add(t["name"], f"{area} sqm × RM {t['low']}–{t['high']}", area * t["low"], area * t["high"], "Structure")
    if has_insul:
        f = PRODUCTS["INS-FOIL"]
        add(f["name"], f"{area} sqm × RM {f['low']}–{f['high']}", area * f["low"], area * f["high"], "Insulation")
    if has_gutter:
        add("Gutter, Flashing & Ridge Set", "6–10% of roof value",
            area * sys["low"] * GUTTER_PCT[0], area * sys["high"] * GUTTER_PCT[1], "Roofing")
    if has_wp:
        w = PRODUCTS["WPG-01"]
        add(w["name"], "per job", w["low"], w["high"], "Repair")
    if carport > 0:
        c = PRODUCTS["CAN-01"]
        add("Solar Carport / Canopy", f"{carport} sqm × RM {c['low']}–{c['high']}", carport * c["low"], carport * c["high"], "Carport")

    scope_low = sum(r["Low"] for r in rows)
    scope_high = sum(r["High"] for r in rows)
    add("Installation & Workmanship", "12–18% of roof scope", scope_low * LABOR_PCT[0], scope_high * LABOR_PCT[1], "Installation")

    roof_low = sum(r["Low"] for r in rows)
    roof_high = sum(r["High"] for r in rows)

    solar_low = solar_high = 0
    if kwp > 0:
        add(f"Solar PV System — {kwp} kWp", f"{kwp} kWp × RM {SOLAR_RATE[0]:,}–{SOLAR_RATE[1]:,}",
            kwp * SOLAR_RATE[0], kwp * SOLAR_RATE[1], "Solar")
        solar_low += kwp * SOLAR_RATE[0]; solar_high += kwp * SOLAR_RATE[1]
    if has_batt:
        add("Battery Storage — 10 kWh", "per unit", BATTERY[0], BATTERY[1], "Solar")
        solar_low += BATTERY[0]; solar_high += BATTERY[1]

    total_low = sum(r["Low"] for r in rows)
    total_high = sum(r["High"] for r in rows)
    mid = (total_low + total_high) / 2

    # ---------------- KPI row ----------------
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Estimate (Mid)", rm(mid))
    k2.metric("Total Range", f"{rm(total_low)} – {rm(total_high)}")
    k3.metric("Roof-Only Range", f"{rm(roof_low)} – {rm(roof_high)}")
    k4.metric("Blended Rate", f"RM {((roof_low + roof_high) / 2) / area:,.0f} /sqm")

    # ---------------- Breakdown table ----------------
    st.subheader("Detailed Material Breakdown")
    df = pd.DataFrame(rows)
    show = df[["Item", "Basis", "Low", "High"]].copy()
    show["Low"] = show["Low"].map(rm)
    show["High"] = show["High"].map(rm)
    total_row = pd.DataFrame([{"Item": "TOTAL ESTIMATE", "Basis": f"{area} sqm roof" + (f" + {kwp} kWp solar" if kwp else ""),
                               "Low": rm(total_low), "High": rm(total_high)}])
    st.dataframe(pd.concat([show, total_row], ignore_index=True), width="stretch", hide_index=True)

    # ---------------- Cost split ----------------
    c_left, c_right = st.columns([1, 1])
    with c_left:
        st.subheader("Where the money goes")
        split = df.assign(Mid=(df["Low"] + df["High"]) / 2).groupby("Group")["Mid"].sum().sort_values(ascending=False)
        st.bar_chart(split, horizontal=True, color="#f5a13d")

    with c_right:
        st.subheader("Solar return estimate")
        if kwp > 0:
            gen_month = kwp * PEAK_SUN * 30 * PERF
            save_month = gen_month * TARIFF
            payback = ((solar_low + solar_high) / 2) / (save_month * 12)
            p1, p2, p3 = st.columns(3)
            p1.metric("Generation / mo", f"{gen_month:,.0f} kWh")
            p2.metric("Bill saving / mo", rm(save_month))
            p3.metric("Simple payback", f"{payback:.1f} yrs")
            st.caption("Assumes 4.5 peak sun hours, 80% performance ratio, RM 0.34/kWh average tariff. "
                       "Actual results vary with orientation, shading, weather and SESB tariff band.")
        else:
            st.info("Add a solar package in the sidebar to see generation and payback estimates.")

    # ---------------- Catalog ----------------
    st.subheader("Product / Solution Catalog")
    cat_df = pd.DataFrame([
        dict(Product=p["name"], Category=p["cat"],
             Estimate=(f"RM {p['low']:,} – {p['high']:,} / job" if p.get("per_job") else f"RM {p['low']} – {p['high']} / sqm"),
             Heat=p["heat"], Noise=p["noise"], Durability=p["dur"], **{"Best For": p["best"]})
        for p in PRODUCTS.values()
    ])
    cats = st.multiselect("Filter category", sorted(cat_df["Category"].unique()))
    st.dataframe(cat_df[cat_df["Category"].isin(cats)] if cats else cat_df,
                 width="stretch", hide_index=True)

    # ---------------- Lead / WhatsApp ----------------
    st.subheader("Send your estimate to WhatsApp")
    l1, l2 = st.columns(2)
    name = l1.text_input("Name")
    loc = l2.text_input("Project Location", placeholder="e.g. Penampang, Kota Kinabalu")

    lines = ["SOLA ROOF — Estimate Request"]
    if name: lines.append(f"Name: {name}")
    if loc: lines.append(f"Location: {loc}")
    lines += [f"Building: {building}", f"Roof area: {area} sqm", f"System: {sys['name']}"]
    if has_truss: lines.append("+ Steel truss")
    if has_insul: lines.append("+ Foil insulation")
    if has_gutter: lines.append("+ Gutter/flashing set")
    if has_wp: lines.append("+ Waterproofing package")
    lines.append(f"Solar: {kwp} kWp" + (" + 10kWh battery" if has_batt else "") if kwp else "Solar: none")
    if carport: lines.append(f"Carport: {carport} sqm")
    lines += ["", f"Estimated range: {rm(total_low)} - {rm(total_high)}",
              "(Sample estimate only - please advise site visit for formal quote)"]
    msg = "\n".join(lines)

    st.code(msg)
    st.link_button("📲 Open in WhatsApp", f"https://wa.me/60123456789?text={quote(msg)}")

    st.divider()
    st.caption("SOLA ROOF · Kota Kinabalu, Sabah · Sample dashboard — all figures are indicative ranges, not a formal quotation.")


# ================================================================
# Navigation
# ================================================================
nav = st.navigation([
    st.Page(showcase, title="Animated Showcase", icon="▶️", url_path="showcase", default=True),
    st.Page(estimator, title="Cost Estimator", icon="🧮", url_path="estimator"),
])
nav.run()
