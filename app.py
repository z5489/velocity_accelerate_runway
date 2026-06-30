from flask import Flask, jsonify, request, send_from_directory
import pandas as pd
import numpy as np
import glob
import os
import re
import random
from datetime import datetime
import yfinance as yf

app = Flask(__name__, static_folder='static', static_url_path='/static')

# --- Indicator Functions ---
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).copy()
    loss = (-delta.where(delta < 0, 0)).copy()
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi

# --- Data Loading ---
def load_cohort(selected_date, universe_prefix="summary"):
    cohort_list = []
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
            if universe_prefix == "summary":
                summary_files = glob.glob(f"batch_summary_*_{selected_date}.csv")
            else:
                universe_name = universe_prefix.replace("summary_", "")
                summary_files = glob.glob(f"batch_summary_{universe_name}_*_{selected_date}.csv")
    
    if summary_files:
        for filepath in summary_files:
            try:
                sdf = pd.read_csv(filepath)
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
    return cohort_list

def get_available_dates(universe_prefix="summary"):
    dates = set()
    output_summaries = glob.glob(os.path.join("output", f"{universe_prefix}_*.csv"))
    for f in output_summaries:
        match = re.search(rf"{universe_prefix}_(\d{{4}}-\d{{2}}-\d{{2}})\.csv$", f)
        if match:
            dates.add(match.group(1))
    if universe_prefix == "summary":
        batch_summaries = glob.glob("batch_summary_*_*.csv")
        for f in batch_summaries:
            match = re.search(r"batch_summary_\d+_(\d{4}-\d{2}-\d{2})\.csv$", f)
            if match:
                dates.add(match.group(1))
    else:
        universe_name = universe_prefix.replace("summary_", "")
        batch_summaries = glob.glob(f"batch_summary_{universe_name}_*_*.csv")
        for f in batch_summaries:
            match = re.search(rf"batch_summary_{universe_name}_\d+_(\d{{4}}-\d{{2}}-\d{{2}})\.csv$", f)
            if match:
                dates.add(match.group(1))
    if os.path.exists(os.path.join("output", f"{universe_prefix}_local.csv")):
        dates.add("local")
    elif universe_prefix == "summary" and os.path.exists("batch_summary_local.csv"):
        dates.add("local")
    return sorted(list(dates), reverse=True) if dates else []

def compute_scores(cohort_list, mode):
    if not cohort_list:
        return []
    scored_cohort = []
    for item in cohort_list:
        ticker = item['ticker']
        v_raw = item['velocity']
        a_raw = item['acceleration']
        rsi_raw = item['rsi']
        if mode == "Bearish Short":
            v_score = min(100.0, max(0.0, (-v_raw / 5.0) * 100.0))
            a_score = 100.0 if a_raw < 0 else 30.0
            r_score = 100.0 * np.exp(-((rsi_raw - 70.0) ** 2) / (2.0 * (15.0 ** 2)))
            w_v, w_a, w_r = 0.35, 0.35, 0.30
        else:
            v_score = min(100.0, max(0.0, (v_raw / 5.0) * 100.0))
            a_score = 100.0 if a_raw > 0 else 30.0
            if mode == "Aggressive Momentum Chaser":
                r_score = 100.0 if rsi_raw <= 80 else max(0.0, 100.0 * (100.0 - rsi_raw) / 20.0)
                w_v, w_a, w_r = 0.40, 0.40, 0.20
            elif mode == "Balanced Swing Trader":
                r_score = 100.0 * np.exp(-((rsi_raw - 60.0) ** 2) / (2.0 * (15.0 ** 2)))
                w_v, w_a, w_r = 0.35, 0.35, 0.30
            else:
                r_score = 100.0 if rsi_raw <= 30 else max(0.0, 100.0 * (100.0 - rsi_raw) / 70.0)
                w_v, w_a, w_r = 0.15, 0.35, 0.50
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
    return sorted(scored_cohort, key=lambda x: x['Total Score'], reverse=True)

def get_chart_data(ticker, period="6mo"):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty:
            return None
        df = df.copy()
        df['Date'] = df.index.strftime('%Y-%m-%d')
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        df = df.dropna(subset=['MA50'])
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).copy()
        loss = (-delta.where(delta < 0, 0)).copy()
        avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))
        return df.to_dict('records')
    except Exception:
        return None

# --- API Routes ---
@app.route('/api/cohort')
def api_cohort():
    universe = request.args.get('universe', 'US Stocks')
    date = request.args.get('date', '')
    mode = request.args.get('mode', 'Balanced Swing Trader')
    universe_prefix = "summary" if universe == "US Stocks" else "summary_uk_etfs"
    cohort_list = load_cohort(date, universe_prefix)
    scored = compute_scores(cohort_list, mode)
    return jsonify({'cohort': scored, 'count': len(scored)})

@app.route('/api/chart')
def api_chart():
    ticker = request.args.get('ticker', '')
    period = request.args.get('period', '6mo')
    data = get_chart_data(ticker, period)
    if data:
        return jsonify({'data': data, 'ticker': ticker})
    return jsonify({'error': 'No data found'}), 404

@app.route('/api/dates')
def api_dates():
    universe = request.args.get('universe', 'US Stocks')
    universe_prefix = "summary" if universe == "US Stocks" else "summary_uk_etfs"
    dates = get_available_dates(universe_prefix)
    return jsonify({'dates': dates})

@app.route('/api/top-ticker')
def api_top_ticker():
    universe = request.args.get('universe', 'US Stocks')
    date = request.args.get('date', '')
    mode = request.args.get('mode', 'Balanced Swing Trader')
    universe_prefix = "summary" if universe == "US Stocks" else "summary_uk_etfs"
    cohort_list = load_cohort(date, universe_prefix)
    scored = compute_scores(cohort_list, mode)
    if scored:
        top_score = scored[0]['Total Score']
        top_candidates = [x for x in scored if x['Total Score'] == top_score]
        top = random.choice(top_candidates)
        return jsonify({'ticker': top['Ticker'], 'score': top['Total Score'], 'name': top['Name']})
    return jsonify({'ticker': '', 'score': 0, 'name': ''})

# --- Frontend ---
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    # Only run Flask when not run via Streamlit
    try:
        import streamlit as st
        is_streamlit = st.runtime.exists()
    except (ImportError, AttributeError):
        is_streamlit = False
        
    if not is_streamlit:
        app.run(debug=True, port=5000)

# Streamlit redirect execution
try:
    import streamlit as st
    is_streamlit = st.runtime.exists()
except (ImportError, AttributeError):
    is_streamlit = False

if is_streamlit:
    import dashboard
