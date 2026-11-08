import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import gc # Added for memory management

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Telco Network Dashboard", page_icon="📡", layout="wide")

# --- CSS TO FIX EVERYTHING & CREATE CENTERED SHADOW NAVIGATION ---
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] { background-color: #FFFFFF; }
        [data-testid="stHeader"] { background-color: rgba(0,0,0,0); z-index: 1000; }
        
        /* Force text to black globally */
        .stMarkdown, p, span, h1, h2, h3, h4, h5, h6, label, div { color: #000000 !important; }

        .floating-header {
            position: fixed; top: 0; left: 0; width: 100%; z-index: 998;   
            background-color: #FFFFFF !important; padding: 15px 40px; box-sizing: border-box;
            border-bottom: 1px solid #EAEAEA; box-shadow: 0px 10px 20px -10px rgba(0, 0, 0, 0.1); text-align: right; 
        }
        .header-title { font-size: 2rem; font-weight: 900; margin: 0; color: #000000 !important; }
        .header-subtitle { font-size: 1rem; color: #555555 !important; margin-top: 5px; }

        .block-container { padding-top: 130px !important; padding-bottom: 100px !important; }
        
        .kpi-card {
            background-color: #F8F9FA; border: 1px solid #E9ECEF; border-radius: 10px;
            padding: 20px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
        .kpi-title { font-size: 1rem; font-weight: 600; color: #495057 !important; margin-bottom: 5px;}
        .kpi-value { font-size: 2rem; font-weight: 800; color: #212529 !important; margin: 0;}
        
        /* Sidebar Base Styling */
        [data-testid="stSidebar"] {
            background-color: #F8F9FA; border-right: 1px solid #EAEAEA; z-index: 1001; 
        }

        /* Sidebar Filters */
        [data-testid="stSidebar"] .stExpander {
            background-color: #E2E8F0 !important; border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important; margin-bottom: 15px;
        }
        [data-testid="stSidebar"] .stExpander summary {
            background-color: #E2E8F0 !important; border-radius: 8px !important;
            padding: 10px !important; color: #000000 !important; font-weight: 600 !important;
        }
        [data-testid="stSidebar"] .stCheckbox label p { color: #1E293B !important; font-weight: 500 !important; }
        [data-testid="stSidebar"] .stCheckbox div[data-baseweb="checkbox"] > div:first-child { border-color: #FCA5A5 !important; }
        [data-testid="stSidebar"] .stCheckbox div[data-baseweb="checkbox"][data-checked="true"] > div:first-child {
            background-color: #FCA5A5 !important; border-color: #FCA5A5 !important;
        }

        /* Buttons */
        .stButton > button {
            background-color: #E2E8F0 !important; color: #000000 !important;
            border: 1px solid #CBD5E1 !important; border-radius: 8px !important;
            font-weight: bold !important; width: 100%; padding: 10px 20px !important;
        }
        .stButton > button:hover { background-color: #CBD5E1 !important; border-color: #94A3B8 !important; }
        
        /* FIXED NAVIGATION BAR */
        div[data-testid="stRadio"] > div[role="radiogroup"] {
            display: flex !important;
            flex-direction: row !important;
            justify-content: center !important;
            flex-wrap: nowrap !important;
            background-color: #F1F5F9 !important;
            padding: 8px 15px !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06) !important;
            gap: 10px !important;
        }
        div[data-testid="stRadio"] input[type="radio"] { display: none !important; }
        div[data-testid="stRadio"] div[data-baseweb="radio"] > div:first-child { display: none !important; }
        div[data-testid="stRadio"] label {
            background-color: transparent !important;
            padding: 10px 20px !important;
            border-radius: 8px !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            margin: 0 !important;
            width: auto !important;
        }
        div[data-testid="stRadio"] label:hover { background-color: #E2E8F0 !important; }
        div[data-testid="stRadio"] label[data-checked="true"] {
            background-color: #FCA5A5 !important; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        }
        div[data-testid="stRadio"] label p {
            color: #1E293B !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            margin: 0 !important;
            white-space: nowrap !important;
        }
        div[data-testid="stRadio"] label[data-checked="true"] p {
            color: #000000 !important;
            font-weight: 800 !important;
        }

        /* Fixed Footer */
        .footer {
            position: fixed; bottom: 0; left: 0; width: 100%;
            background-color: #FFFFFF; text-align: center; color: #555555; 
            font-size: 14px; padding: 15px 0;
            border-top: 1px solid #EAEAEA; z-index: 999;
        }
    </style>

    <div class="floating-header">
        <div class="header-title">📡 Telco Network Dashboard</div>
        <div class="header-subtitle">Deep-dive analytics into signal coverage, quality, and cell tower performance.</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. LOAD & CLEAN DATA (OPTIMIZED FOR MEMORY) ---
@st.cache_data(show_spinner="Loading and processing network data...")
def load_data():
    try:
        cols_to_use = [
            "Current Date Time", "Latitude", "Longitude", "dBm", 
            "RSRP LTE", "SNR LTE", "PCI LTE", "Network Operator", 
            "Network Type", "Band"
        ]
        dtypes = {
            "dBm": "float32", "RSRP LTE": "float32", "SNR LTE": "float32", 
            "Latitude": "float32", "Longitude": "float32"
        }
        df = pd.read_csv(
            "TelcoNetwork_Dataset_MagnoGrijaldo.csv", 
            usecols=lambda c: c.strip() in cols_to_use,
            dtype=dtypes,
            on_bad_lines="skip"
        )
    except FileNotFoundError:
        st.error("Dataset not found. Please ensure 'TelcoNetwork_Dataset_MagnoGrijaldo.csv' is in the same folder.")
        st.stop()
    except ValueError:
        df = pd.read_csv("TelcoNetwork_Dataset_MagnoGrijaldo.csv", on_bad_lines="skip")
        df.columns = [c.strip() for c in df.columns]

    df.columns = [c.strip() for c in df.columns]
    
    for col in ["Network Operator", "Network Type", "Band"]:
        if col in df.columns:
            df[col] = df[col].astype("category")
            
    if "Current Date Time" in df.columns:
        df["Current Date Time"] = pd.to_datetime(df["Current Date Time"], errors="coerce")
    
    def fix_coord_vectorized(series):
        mask = (series < -90) | (series > 90) if "Lat" in series.name else (series < -180) | (series > 180)
        str_vals = series[mask].abs().astype(int).astype(str)
        fixed_vals = pd.to_numeric(str_vals.str[0] + "." + str_vals.str[1:], errors="coerce") * -1
        return series.where(~mask, fixed_vals)

    if "Latitude" in df.columns and "Longitude" in df.columns:
        df["Latitude"] = fix_coord_vectorized(df["Latitude"])
        df["Longitude"] = fix_coord_vectorized(df["Longitude"])
        df = df.dropna(subset=["Latitude", "Longitude", "dBm"])
    
    conditions = [
        (df["dBm"] >= -85),
        (df["dBm"] >= -95) & (df["dBm"] < -85),
        (df["dBm"] >= -105) & (df["dBm"] < -95),
        (df["dBm"] < -105)
    ]
    choices = ["Excellent (>= -85)", "Good (-86 to -95)", "Fair (-96 to -105)", "Poor (<= -106)"]
    df["Quality"] = np.select(conditions, choices, default="Unknown")
    df["Quality"] = df["Quality"].astype("category")

    gc.collect()
    return df

df = load_data()

# --- 3. SIDEBAR FILTERS ---
st.sidebar.header("Data Filters")
st.sidebar.markdown("<br>", unsafe_allow_html=True)

def create_checkbox_filter(title, options):
    with st.sidebar.expander(title, expanded=False):
        select_all = st.checkbox("Select All", value=True, key=f"all_{title}")
        selected = []
        for opt in options:
            if select_all:
                st.checkbox(str(opt), value=True, disabled=True, key=f"disabled_{title}_{opt}")
                selected.append(opt)
            else:
                if st.checkbox(str(opt), value=False, key=f"active_{title}_{opt}"):
                    selected.append(opt)
        return selected

operator_filter = create_checkbox_filter("Network Operator (MNC)", df["Network Operator"].dropna().unique())
net_type_filter = create_checkbox_filter("Network Type", df["Network Type"].dropna().unique())
band_filter = create_checkbox_filter("Frequency Band", sorted(df["Band"].dropna().unique()))

filtered_df = df[
    (df["Network Operator"].isin(operator_filter)) & 
    (df["Network Type"].isin(net_type_filter)) &
    (df["Band"].isin(band_filter))
]

if filtered_df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# --- GLOBAL CHART STYLE ---
def apply_chart_style(fig, title_text="", is_pie=False):
    fig.update_layout(
        template="plotly_white", plot_bgcolor="#FCFCFC", paper_bgcolor="#FCFCFC",  
        title=dict(text=title_text, font=dict(color="black", size=16)), margin=dict(l=60, r=40, t=60, b=60),
        font=dict(color="black"), legend=dict(font=dict(color="black"), bgcolor="white", bordercolor="black", borderwidth=1)
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', gridcolor='#D3D3D3', tickfont=dict(color="black"))
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black', gridcolor='#D3D3D3', tickfont=dict(color="black"))
    if not is_pie:
        fig.update_layout(shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=1, line=dict(color="black", width=2), fillcolor="rgba(0,0,0,0)")])
    return fig

# --- 4. CENTERED NAVIGATION BAR ---
spacer_left, nav_col, spacer_right = st.columns([1.5, 2, 1.5])

with nav_col:
    nav_selection = st.radio(
        "Navigation",
        options=["📊 Network Overview", "📍 Coverage Map", "🛠️ Prescriptive Analytics"],
        horizontal=True,
        label_visibility="collapsed" 
    )

# ==========================================
# PAGE 1: OVERVIEW
# ==========================================
if nav_selection == "📊 Network Overview":
    st.subheader("Network Overview KPIs")
    st.markdown("A high-level summary of the network's current health, based on the filtered dataset.")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1: st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Samples</div><div class="kpi-value">{len(filtered_df):,}</div></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="kpi-card"><div class="kpi-title">Avg Signal (RSRP)</div><div class="kpi-value">{filtered_df["RSRP LTE"].mean():.1f} dBm</div></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="kpi-card"><div class="kpi-title">Avg Quality (SINR)</div><div class="kpi-value">{filtered_df["SNR LTE"].mean():.1f} dB</div></div>', unsafe_allow_html=True)
    with col4: st.markdown(f'<div class="kpi-card"><div class="kpi-title">Unique Cell Towers (PCI)</div><div class="kpi-value">{filtered_df["PCI LTE"].nunique()}</div></div>', unsafe_allow_html=True)

    st.divider()

    st.subheader("Signal Quality Distribution")
    st.markdown("This section breaks down the overall network quality. The **pie chart** shows the proportion of samples in each quality tier, while the **scatter plot** maps raw signal strength (RSRP) against signal quality (SINR). The dashed lines represent standard thresholds for acceptable performance.")
    
    color_map = {"Excellent (>= -85)": "#00CC96", "Good (-86 to -95)": "#636EFA", "Fair (-96 to -105)": "#EF553B", "Poor (<= -106)": "#FFA15A"}
    col_q1, col_q2 = st.columns([1, 2])
    
    with col_q1:
        qc = filtered_df["Quality"].value_counts().reset_index()
        qc.columns = ["Quality", "Count"]
        fig_pie = px.pie(qc, names="Quality", values="Count", hole=0.5, color="Quality", color_discrete_map=color_map)
        st.plotly_chart(apply_chart_style(fig_pie, "Quality Distribution", is_pie=True), use_container_width=True)
        
    with col_q2:
        fig_scatter = px.scatter(filtered_df, x="RSRP LTE", y="SNR LTE", color="Quality", opacity=0.6, color_discrete_map=color_map)
        fig_scatter.add_vline(x=-95, line_dash="dash", line_color="black")
        fig_scatter.add_hline(y=0, line_dash="dash", line_color="black")
        st.plotly_chart(apply_chart_style(fig_scatter, "Signal Strength vs Quality"), use_container_width=True)
    
    st.divider()
    with st.expander("🗄️ View Cleaned & Filtered Data"):
        st.markdown("Explore the raw data points that make up the charts above. You can sort by any column or download the data directly.")
        st.dataframe(filtered_df, use_container_width=True)

# ==========================================
# PAGE 2: MAP ONLY
# ==========================================
elif nav_selection == "📍 Coverage Map":
    st.subheader("📍 Geographic Signal Coverage Map")
    st.write("Explore signal strength across different locations. Darker dots represent weaker signals, brighter dots represent stronger signals. Hover over a point to see the exact signal strength (dBm) and coordinates.")
    
    if len(filtered_df) > 1500:
        map_df = filtered_df.sample(n=1500, random_state=42)
        st.info("Showing a sample of 1,500 points to ensure smooth browser performance.")
    else:
        map_df = filtered_df

    fig_map = px.scatter_map(map_df, lat="Latitude", lon="Longitude", color="dBm", zoom=11,
                             color_continuous_scale=px.colors.sequential.Viridis, map_style="carto-positron",
                             hover_data={"Latitude": True, "Longitude": True, "dBm": True})
    fig_map.update_traces(marker=dict(size=12))
    fig_map.update_layout(
        template="plotly_white", margin=dict(l=0, r=0, t=0, b=0), height=700, 
        map_center={"lat": -3.04, "lon": -60.00},
        coloraxis_colorbar=dict(title=dict(text="Signal (dBm)", font=dict(color="black")), tickfont=dict(color="black"))
    )
    st.plotly_chart(fig_map, use_container_width=True)

# ==========================================
# PAGE 3: PRESCRIPTIVE ANALYTICS ONLY
# ==========================================
elif nav_selection == "🛠️ Prescriptive Analytics":
    st.header("🛠️ Network Optimization Engine")
    st.markdown("""
    This engine analyzes historical performance from your dataset to provide **prescriptive recommendations**. 
    By calculating the statistical average of **Signal Strength (RSRP)** and **Quality (SINR)** across different Frequency Bands, 
    we can recommend the optimal configuration for a specific scenario.
    """)

    band_performance = filtered_df.groupby("Band", observed=True).agg({
        "RSRP LTE": "mean",
        "SNR LTE": "mean",
        "dBm": "count"
    }).rename(columns={"dBm": "Sample Count"}).reset_index()

    best_band_signal = band_performance.sort_values(by="RSRP LTE", ascending=False).iloc[0]
    best_band_quality = band_performance.sort_values(by="SNR LTE", ascending=False).iloc[0]

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown("### 📊 Data-Driven Baseline")
        st.markdown("The chart below shows the average raw signal strength (RSRP) for each frequency band in your dataset. This serves as the baseline for the recommendations provided in the simulator.")
        st.info(f"**Historical Best Band for Raw Signal:** Band {best_band_signal['Band']} (Avg: {best_band_signal['RSRP LTE']:.1f} dBm)\n\n"
                f"**Historical Best Band for Clean Quality:** Band {best_band_quality['Band']} (Avg: {best_band_quality['SNR LTE']:.1f} dB)")
        
        fig_band = px.bar(band_performance.sort_values(by="RSRP LTE", ascending=False), 
                          x="Band", y="RSRP LTE", color="RSRP LTE", color_continuous_scale="Blues",
                          title="Average RSRP by Band (Basis for Recommendation)")
        st.plotly_chart(apply_chart_style(fig_band), use_container_width=True)

    with col_p2:
        st.markdown("### 🤖 Network Scenario Simulator")
        st.write("Input your current network metrics below to receive an actionable recommendation based on the dataset's historical performance.")
        
        bands_list = sorted(df['Band'].dropna().unique())
        current_band = st.radio("Current Frequency Band", options=bands_list, horizontal=True)
        current_signal = st.slider("Current Signal Strength (RSRP dBm)", min_value=-120, max_value=-60, value=-105)
        current_snr = st.slider("Current Quality (SINR dB)", min_value=-20, max_value=30, value=2)
        
        submit = st.button("Generate Recommendation")
            
        if submit:
            st.markdown("---")
            st.markdown("#### 📋 Optimization Report")
            
            if current_signal >= -85:
                st.success(f"**Current Status:** Excellent signal. Your connection on Band {current_band} is optimal.")
            elif current_signal >= -95:
                st.info(f"**Current Status:** Good signal. Band {current_band} is performing adequately.")
            elif current_signal >= -105:
                st.warning(f"**Current Status:** Fair signal. You may experience intermittent drops.")
            else:
                st.error(f"**Current Status:** Poor signal. Immediate action recommended.")
                
            st.write("**Prescriptive Actions based on Dataset:**")
            
            if current_snr < 0:
                st.markdown(f"- **Interference Mitigation:** Your SINR is very low ({current_snr} dB), indicating heavy noise. The data shows that **Band {best_band_quality['Band']}** historically provides the cleanest signal (Avg SINR: {best_band_quality['SNR LTE']:.1f} dB). **Recommendation:** Force your device to lock onto Band {best_band_quality['Band']}.")
            elif current_signal < -105:
                st.markdown(f"- **Coverage Optimization:** Your RSRP is weak. The data shows that **Band {best_band_signal['Band']}** provides the strongest raw signal (Avg RSRP: {best_band_signal['RSRP LTE']:.1f} dBm). **Recommendation:** Switch to Band {best_band_signal['Band']} if available in your area.")
            else:
                st.markdown(f"- **Maintain Configuration:** Current metrics are within acceptable thresholds. No band switching is prescribed by the data at this time.")
                
            if current_band != best_band_quality['Band'] and current_snr < 10:
                 st.markdown(f"- **Alternative:** Try a different network operator. The dataset shows varying performance across MNCs. (Best operator average: {filtered_df.groupby('Network Operator', observed=True)['SNR LTE'].mean().idxmax()}).")

# --- 5. FIXED FOOTER ---
st.markdown("""
    <div class="footer">
        <p style="margin: 0;"><strong>Telco Network Dashboard</strong> &nbsp;|&nbsp; © 2026 Magno & Grijaldo. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)