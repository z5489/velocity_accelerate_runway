import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import glob
import os
import re
import random
from datetime import datetime

# Set page config
st.set_page_config(
    layout="wide",
    page_title="Hologram | Quant Trading Signals",
    page_icon="📈"
)

# Custom Sleek Dark Theme with Glassmorphism and Custom Typography (Outfit)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');

/* Base Styles */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    font-family: 'Outfit', sans-serif;
    background: radial-gradient(circle at top right, #111827, #030712) !important;
    color: #f3f4f6 !important;
}

/* Sidebar Custom Styling */
[data-testid="stSidebar"] {
    background-color: #0b0f19 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    padding-top: 2rem;
}

/* Typography Overrides */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
}

/* Sidebar Headings */
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
    color: #38bdf8 !important;
    font-weight: 600 !important;
}

/* Custom Profile Indicator Badge */
.profile-indicator {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.5));
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(12px);
}

.profile-title {
    font-size: 0.8rem;
    color: #38bdf8;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 700;
    margin-bottom: 0.4rem;
}

.profile-name {
    font-size: 1.8rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 0.5rem;
    background: linear-gradient(90deg, #ffffff, #ffffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.profile-weights {
    display: flex;
    gap: 1rem;
    margin-top: 0.8rem;
    font-size: 0.85rem;
}

.weight-tag {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 2px 8px;
    border-radius: 8px;
    color: #ffffff;
}

.weight-tag span {
    color: #38bdf8;
    font-weight: 600;
}

/* Top Setup Banner Styles */
.top-setup-banner {
    position: relative;
    border-radius: 16px;
    padding: 1.75rem;
    margin-bottom: 2.5rem;
    overflow: hidden;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: all 0.3s ease;
}

.top-setup-banner.success {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(56, 189, 248, 0.08) 100%);
    border-left: 6px solid #10b981;
}

.top-setup-banner.neutral {
    background: linear-gradient(135deg, rgba(55, 65, 81, 0.4) 0%, rgba(31, 41, 55, 0.2) 100%);
    border-left: 6px solid #6b7280;
}

.banner-badge {
    display: inline-block;
    padding: 4px 10px;
    font-size: 0.75rem;
    font-weight: 700;
    border-radius: 6px;
    margin-bottom: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.banner-badge.success {
    background-color: rgba(16, 185, 129, 0.2);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.banner-badge.neutral {
    background-color: rgba(107, 114, 128, 0.2);
    color: #d1d5db;
    border: 1px solid rgba(107, 114, 128, 0.3);
}

.top-setup-banner h2 {
    margin: 0 0 0.5rem 0;
    color: white;
    font-size: 1.6rem;
    font-weight: 700;
}

.top-setup-banner p {
    margin: 0;
    color: #ffffff;
    font-size: 1rem;
}

/* Custom styled Metric Cards for Deep-Dive */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    margin-bottom: 2.5rem;
}

.custom-metric-card {
    background: rgba(17, 24, 39, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(12px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.custom-metric-card:hover {
    transform: translateY(-2px);
    border-color: rgba(56, 189, 248, 0.3);
    box-shadow: 0 15px 35px -10px rgba(56, 189, 248, 0.1);
}

.metric-header {
    font-size: 0.85rem;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
    margin-bottom: 0.75rem;
}

.metric-val {
    font-size: 2.2rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
}

.metric-sub {
    font-size: 0.9rem;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 8px;
}

.metric-badge {
    background: linear-gradient(135deg, #0284c7, #0ea5e9);
    color: white;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
}

/* Subtle Divider */
hr {
    border: 0;
    height: 1px;
    background: linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,0.08) 50%, rgba(255,255,255,0));
    margin: 2.5rem 0;
}

/* Ensure high contrast white text for readability against dark backgrounds */
[data-testid="stSidebar"] label, 
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] span, 
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3,
.profile-indicator *, 
.top-setup-banner *, 
.custom-metric-card *,
.stMarkdown p, 
.stMarkdown span,
.stMarkdown li,
.stMarkdown h1,
.stMarkdown h2,
.stMarkdown h3 {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)


# Mathematical indicator functions
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).copy()
    loss = (-delta.where(delta < 0, 0)).copy()
    
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi


# Fetch & calculate all metrics (Cached)
@st.cache_data(ttl=600)
def fetch_and_prepare_all_data(selected_date, universe_prefix="summary"):
    cohort_list = []
    
    # 1. Search for aggregated summary file or batch files for the selected date
    if selected_date == "local":
        summary_file = os.path.join("output", f"{universe_prefix}_local.csv")
        if os.path.exists(summary_file):
            summary_files = [summary_file]
        elif os.path.exists(f"batch_summary_{universe_prefix}_local.csv"):
            summary_files = [f"batch_summary_{universe_prefix}_local.csv"]
        elif universe_prefix == "summary" and os.path.exists("batch_summary_local.csv"):
            summary_files = ["batch_summary_local.csv"]
        else:
            summary_files = []
    else:
        summary_file = os.path.join("output", f"{universe_prefix}_{selected_date}.csv")
        if os.path.exists(summary_file):
            summary_files = [summary_file]
        else:
            # Handle fallback to batch files if present
            if universe_prefix == "summary":
                summary_files = glob.glob(f"batch_summary_*_{selected_date}.csv")
            else:
                universe_name = universe_prefix.replace("summary_", "")
                summary_files = glob.glob(f"batch_summary_{universe_name}_*_{selected_date}.csv")
        
    if summary_files:
        for filepath in summary_files:
            try:
                sdf = pd.read_csv(filepath)
                # Ensure we have the required columns
                required_cols = {'ticker', 'close', 'velocity', 'acceleration', 'rsi'}
                if required_cols.issubset(sdf.columns):
                    for _, row in sdf.iterrows():
                        cohort_list.append({
                            'ticker': str(row['ticker']),
                            'name': str(row.get('name', row['ticker'])),
                            'sector': str(row.get('sector', 'N/A')),
                            'industry': str(row.get('industry', 'N/A')),
                            'close': float(row['close']),
                            'velocity': float(row['velocity']),
                            'acceleration': float(row['acceleration']),
                            'rsi': float(row['rsi']),
                            'region': str(row.get('region', 'UK' if universe_prefix == 'summary_uk_etfs' else 'US'))
                        })
            except Exception:
                pass
                
    # Return empty dict for all_data to preserve unpacking signature: all_data, cohort_list
    return {}, cohort_list


# Calculation of final scoring based on Mode
def compute_scores(cohort_list, mode):
    if not cohort_list:
        return []

    scored_cohort = []
    for item in cohort_list:
        ticker = item['ticker']
        v_raw = item['velocity']
        a_raw = item['acceleration']
        rsi_raw = item['rsi']

        # Velocity Score — fixed absolute threshold:
        # Any 5-day ROC >= 5% is a perfect 100; scales linearly below that.
        v_score = min(100.0, max(0.0, (v_raw / 5.0) * 100.0))

        # Acceleration Score — fixed absolute threshold:
        # Any positive MACD hist delta (momentum increasing) = 100; negative = 30.
        a_score = 100.0 if a_raw > 0 else 30.0

        # Runway Scores (Continuous functions based on active profile)
        if mode == "Aggressive Momentum Chaser":
            if rsi_raw <= 80:
                r_score = 100.0
            else:
                r_score = max(0.0, 100.0 * (100.0 - rsi_raw) / 20.0)
            w_v, w_a, w_r = 0.40, 0.40, 0.20

        elif mode == "Balanced Swing Trader":
            # Gaussian peak at RSI 60
            r_score = 100.0 * np.exp(-((rsi_raw - 60.0) ** 2) / (2.0 * (15.0 ** 2)))
            w_v, w_a, w_r = 0.35, 0.35, 0.30

        else:  # Mean-Reversion Trader
            # Higher score for lower RSI
            if rsi_raw <= 30:
                r_score = 100.0
            else:
                r_score = max(0.0, 100.0 * (100.0 - rsi_raw) / 70.0)
            w_v, w_a, w_r = 0.15, 0.35, 0.50

        # Total probability score calculation
        total_score = w_v * v_score + w_a * a_score + w_r * r_score

        scored_cohort.append({
            'Ticker': ticker,
            'Name': item.get('name', ticker),
            'Sector': item.get('sector', 'N/A'),
            'Industry': item.get('industry', 'N/A'),
            'Total Score': round(total_score, 1),
            'Region': item.get('region', 'US'),
            'Velocity Score': round(v_score, 1),
            'Acceleration Score': round(a_score, 1),
            'Runway Score': round(r_score, 1),
            'Close Price': round(item['close'], 2),
            '5-Day ROC %': round(v_raw, 2),
            'MACD Hist Delta': round(a_raw, 5),
            'RSI': round(rsi_raw, 1)
        })

    # Sort from highest to lowest score
    return sorted(scored_cohort, key=lambda x: x['Total Score'], reverse=True)


# Plotly rendering
def create_plotly_chart(df, ticker, mode):
    # Calculate Moving Averages first
    df = df.copy()
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()
    
    # Drop initial NaN rows to prevent Plotly path rendering NaN crashes in the browser
    df = df.dropna(subset=['MA50']).copy()
    
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.08, 
        row_heights=[0.7, 0.3]
    )
    
    # 1. Candlestick Chart
    fig.add_trace(
        go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Candlestick',
            increasing_line_color='#10b981',  # Vibrant emerald green
            decreasing_line_color='#ef4444'   # Vibrant red
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['MA20'], name='20-Day SMA', line=dict(color='#0ea5e9', width=1.5)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['MA50'], name='50-Day SMA', line=dict(color='#a855f7', width=1.5)),
        row=1, col=1
    )
    
    # 2. RSI Chart
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['RSI'],
            name='RSI',
            line=dict(color='#f97316', width=2)
        ),
        row=2, col=1
    )
    
    # Determine bounds based on mode
    if mode == "Aggressive Momentum Chaser":
        rsi_upper, rsi_lower = 80, 30
    elif mode == "Balanced Swing Trader":
        rsi_upper, rsi_lower = 70, 30
    else:
        rsi_upper, rsi_lower = 70, 30
        
    fig.add_hline(y=rsi_upper, line_dash="dash", line_color="#ef4444", line_width=1, row=2, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="#4b5563", line_width=0.8, row=2, col=1)
    fig.add_hline(y=rsi_lower, line_dash="dash", line_color="#10b981", line_width=1, row=2, col=1)
    
    # Update styling
    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=550,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(17, 24, 39, 0.4)',
    )
    
    fig.update_yaxes(title_text="Price", row=1, col=1, gridcolor='rgba(255,255,255,0.05)', showline=True, linecolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100], gridcolor='rgba(255,255,255,0.05)', showline=True, linecolor='rgba(255,255,255,0.1)')
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)', showline=True, linecolor='rgba(255,255,255,0.1)')
    
    return fig


# Streamlit Execution Setup
# ----------------- UNIVERSE SELECTOR SETUP -----------------
st.sidebar.markdown("<h2 style='margin-bottom:0;'>🌌 TICKER UNIVERSE</h2>", unsafe_allow_html=True)
selected_universe = st.sidebar.selectbox("Select Ticker Universe:", ["US Stocks", "UK ETFs"], index=0)

universe_prefix = "summary" if selected_universe == "US Stocks" else "summary_uk_etfs"
universe_name = "summary" if selected_universe == "US Stocks" else "uk_etfs"

# ----------------- DATE SELECTOR SETUP -----------------
import re
dates = set()

# Scan output folder for aggregated summaries of the selected universe
output_summaries = glob.glob(os.path.join("output", f"{universe_prefix}_*.csv"))
for f in output_summaries:
    match = re.search(rf"{universe_prefix}_(\d{{4}}-\d{{2}}-\d{{2}})\.csv$", f)
    if match:
        dates.add(match.group(1))

# Scan root folder for batch summaries (backward compatibility)
if universe_prefix == "summary":
    batch_summaries = glob.glob("batch_summary_*_*.csv")
    for f in batch_summaries:
        match = re.search(r"batch_summary_\d+_(\d{4}-\d{2}-\d{2})\.csv$", f)
        if match:
            dates.add(match.group(1))
else:
    batch_summaries = glob.glob(f"batch_summary_{universe_name}_*_*.csv")
    for f in batch_summaries:
        match = re.search(rf"batch_summary_{universe_name}_\d+_(\d{{4}}-\d{{2}}-\d{{2}})\.csv$", f)
        if match:
            dates.add(match.group(1))

# Also check for local summaries if they exist
if os.path.exists(os.path.join("output", f"{universe_prefix}_local.csv")):
    dates.add("local")
elif universe_prefix == "summary" and os.path.exists("batch_summary_local.csv"):
    dates.add("local")

if dates:
    sorted_dates = sorted(list(dates), reverse=True)
    st.sidebar.markdown("<h2 style='margin-bottom:0;'>📅 ANALYSIS DATE</h2>", unsafe_allow_html=True)
    selected_date_str = st.sidebar.selectbox("Select historical date:", sorted_dates, index=0)
else:
    selected_date_str = datetime.now().strftime('%Y-%m-%d')
    st.sidebar.markdown("<h2 style='margin-bottom:0;'>📅 ANALYSIS DATE</h2>", unsafe_allow_html=True)
    st.sidebar.info(f"No summary CSVs found. Using today's date: {selected_date_str}")

all_data, cohort_list = fetch_and_prepare_all_data(selected_date_str, universe_prefix)

# ----------------- SIDEBAR CONFIG -----------------
st.sidebar.markdown("<h2 style='margin-bottom:0;'>⚙️ PROFILE ENGINE</h2>", unsafe_allow_html=True)
st.sidebar.write("Configure the trading system strategy weights.")

mode_options = [
    "Aggressive Momentum Chaser",
    "Balanced Swing Trader",
    "Mean-Reversion Trader"
]

active_mode = st.sidebar.radio(
    "Select Trading Strategy:",
    mode_options,
    index=1  # Balanced Swing Trader by default
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Universe Status")
st.sidebar.write(f"Active Tickers Loaded: **{len(cohort_list)}**")
if st.sidebar.button("🔄 Force Reload & Fetch"):
    st.cache_data.clear()
    st.rerun()

# Get profile weight text and description
if active_mode == "Aggressive Momentum Chaser":
    w_v, w_a, w_r = 40, 40, 20
    mode_desc = "Focusses on rapid price momentum and acceleration. Runway acts as a safety filter only penalizing overbought conditions (>80 RSI)."
elif active_mode == "Balanced Swing Trader":
    w_v, w_a, w_r = 35, 35, 30
    mode_desc = "Balances active medium-term trends with remaining room to run. Scores peaked near 60 RSI to avoid early entries or extreme overbought states."
else:
    w_v, w_a, w_r = 15, 35, 50
    mode_desc = "Mean-reversion model searching for oversold stock floors (low RSI) that are actively accelerating upwards (MACD delta reversal)."

# ----------------- MAIN LAYOUT -----------------

# Header Section
col_title, col_indicator = st.columns([3, 2])

with col_title:
    st.markdown("<h1 style='font-size:3rem; margin-bottom:0.2rem; color: #ffffff;'>HOLOGRAM</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.15rem; color:#ffffff; margin-top:0;'>High-Performance Quant Trading Signals Dashboard</p>", unsafe_allow_html=True)

with col_indicator:
    st.markdown(f"""
    <div class="profile-indicator">
        <div class="profile-title">Active Profile</div>
        <div class="profile-name">{active_mode}</div>
        <div class="profile-weights">
            <div class="weight-tag">Vel: <span>{w_v}%</span></div>
            <div class="weight-tag">Acc: <span>{w_a}%</span></div>
            <div class="weight-tag">Run: <span>{w_r}%</span></div>
        </div>
        <div style="font-size: 0.82rem; color: #ffffff; margin-top: 0.75rem; font-style: italic; line-height: 1.3;">
            {mode_desc}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Recalculate cohort rankings
scored_cohort = compute_scores(cohort_list, active_mode)
# If multiple tickers share the top score, pick one randomly so all tied tickers get exposure
if scored_cohort:
    top_score = scored_cohort[0]['Total Score']
    top_candidates = [x for x in scored_cohort if x['Total Score'] == top_score]
    top_ticker_data = random.choice(top_candidates)
else:
    top_ticker_data = None

# Banner Setup
if top_ticker_data and top_ticker_data['Total Score'] >= 75.0:
    st.markdown(f"""
    <div class="top-setup-banner success">
        <span class="banner-badge success">🔥 TOP TRADE SETUP FOUND</span>
        <h2>High probability setup detected: <strong>{top_ticker_data['Ticker']}</strong></h2>
        <p>Total Probability Score reaches <strong>{top_ticker_data['Total Score']}/100</strong> under {active_mode} profile parameters.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="top-setup-banner neutral">
        <span class="banner-badge neutral">🛡️ MARKET NOTE</span>
        <h2>Market Note: Preserving cash or waiting for cleaner setups.</h2>
        <p>No asset has cleared the 75/100 threshold score. Proceed with low sizing or stand aside.</p>
    </div>
    """, unsafe_allow_html=True)

# Leaderboard Section
st.markdown("### 🏆 Cohort Leaderboard")
st.write("Ranked based on Total Probability Score using active profile rules. Click on any column to sort.")

# Standard Streamlit interactive dataframe
leaderboard_df = pd.DataFrame(scored_cohort)
if not leaderboard_df.empty:
    # Re-order columns for display
    display_cols = [
        'Ticker', 'Name', 'Region', 'Sector', 'Industry', 'Total Score', 'Close Price', 
        'Velocity Score', 'Acceleration Score', 'Runway Score',
        '5-Day ROC %', 'MACD Hist Delta', 'RSI'
    ]
    st.dataframe(
        leaderboard_df[display_cols],
        width="stretch",
        hide_index=True
    )
else:
    st.warning("No data files available.")

st.markdown("<hr>", unsafe_allow_html=True)

# Deep-Dive Section
st.markdown("### 🔍 Technical Deep-Dive")
st.write("Select a ticker to explore historical chart timelines and signal metrics.")

if scored_cohort:
    tickers_list = [x['Ticker'] for x in scored_cohort]
    # Pre-select the same randomly chosen top ticker shown in the banner
    default_index = tickers_list.index(top_ticker_data['Ticker']) if top_ticker_data and top_ticker_data['Ticker'] in tickers_list else 0
    selected_ticker = st.selectbox(
        "Select Ticker for Profile Analysis:",
        tickers_list,
        index=default_index
    )
    
    # Get details for selected ticker
    ticker_details = next((x for x in scored_cohort if x['Ticker'] == selected_ticker), None)
    # Download and compute metrics for the selected ticker on-demand
    try:
        df_ticker = yf.Ticker(selected_ticker).history(period="2y").reset_index()
        if 'Date' in df_ticker.columns:
            df_ticker['Date'] = pd.to_datetime(df_ticker['Date']).dt.tz_localize(None)
            if selected_date_str != "local":
                try:
                    selected_dt = pd.to_datetime(selected_date_str)
                    df_ticker = df_ticker[df_ticker['Date'] <= selected_dt]
                except Exception:
                    pass
            df_ticker['RSI'] = calculate_rsi(df_ticker['Close'])
    except Exception:
        df_ticker = None
    
    if ticker_details and df_ticker is not None:
        # Create Metric Grid
        st.markdown(f"""
        <div class="metric-grid">
            <div class="custom-metric-card">
                <div class="metric-header">Velocity (5-Day ROC)</div>
                <div class="metric-val">{ticker_details['5-Day ROC %']}%</div>
                <div class="metric-sub">
                    <span class="metric-badge">Score: {ticker_details['Velocity Score']}/100</span>
                </div>
            </div>
            <div class="custom-metric-card">
                <div class="metric-header">Acceleration (MACD Hist Delta)</div>
                <div class="metric-val">{ticker_details['MACD Hist Delta']}</div>
                <div class="metric-sub">
                    <span class="metric-badge">Score: {ticker_details['Acceleration Score']}/100</span>
                </div>
            </div>
            <div class="custom-metric-card">
                <div class="metric-header">Runway (14-Day RSI)</div>
                <div class="metric-val">{ticker_details['RSI']}</div>
                <div class="metric-sub">
                    <span class="metric-badge">Score: {ticker_details['Runway Score']}/100</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display Plotly Chart
        chart_fig = create_plotly_chart(df_ticker, selected_ticker, active_mode)
        st.plotly_chart(chart_fig, use_container_width=True)
        
    else:
        st.error(f"Could not load details for {selected_ticker}")
else:
    st.info("Leaderboard is empty. Load ticker data first.")
