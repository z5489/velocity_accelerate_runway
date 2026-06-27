import os
import argparse
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

# Mathematical indicator functions matching app.py calculations
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).copy()
    loss = (-delta.where(delta < 0, 0)).copy()
    
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices):
    ema12 = prices.ewm(span=12, adjust=False).mean()
    ema26 = prices.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - signal_line
    hist_delta = macd_hist.diff(1)
    return macd_line, signal_line, macd_hist, hist_delta

def get_tickers():
    tickers_file = "tickers.txt"
    if os.path.exists(tickers_file):
        with open(tickers_file, "r") as f:
            tickers = [line.strip().upper() for line in f if line.strip() and not line.strip().startswith("#")]
            if tickers:
                return tickers
    # Default fallback
    return ["TSLA", "MSFT", "AAPL", "NVDA", "AMZN", "GOOGL", "META", "BP.L", "AZN.L", "VOD.L", "LSEG.L"]

def compute_latest_metrics(df):
    try:
        # Standardize columns to lowercase for extraction
        df_cols = {col.lower().strip(): col for col in df.columns}
        
        close_key = None
        for col in ['adj close', 'close']:
            if col in df_cols:
                close_key = df_cols[col]
                break
        if not close_key:
            return None
            
        prices = pd.to_numeric(df[close_key], errors='coerce').dropna().reset_index(drop=True)
        if len(prices) < 35:
            return None
            
        # Calculate RSI
        rsi = calculate_rsi(prices)
        
        # Calculate MACD
        _, _, _, hist_delta = calculate_macd(prices)
        
        # Latest Close
        latest_idx = prices.index[-1]
        close_val = prices.iloc[latest_idx]
        
        # Velocity: 5-Day ROC %
        if len(prices) >= 6:
            v_val = ((close_val - prices.iloc[-6]) / prices.iloc[-6]) * 100
        else:
            v_val = 0.0
            
        a_val = hist_delta.iloc[latest_idx]
        rsi_val = rsi.iloc[latest_idx]
        
        if np.isnan(v_val): v_val = 0.0
        if np.isnan(a_val): a_val = 0.0
        if np.isnan(rsi_val): rsi_val = 50.0
        
        return {
            'close': float(close_val),
            'velocity': float(v_val),
            'acceleration': float(a_val),
            'rsi': float(rsi_val)
        }
    except Exception as e:
        print(f"Error computing indicators for ticker: {str(e)}")
        try:
            print(f"df columns: {list(df.columns)}")
            print(f"close_key: {close_key}")
            if close_key and close_key in df.columns:
                print(f"df[close_key] type: {type(df[close_key])}")
                if isinstance(df[close_key], pd.DataFrame):
                    print(f"df[close_key] columns: {list(df[close_key].columns)}")
        except Exception as inner_e:
            print(f"Failed to print debug info: {str(inner_e)}")
        return None

def fetch_single_ticker(ticker):
    try:
        # Download 2 years of daily data using Ticker.history for thread safety
        df = yf.Ticker(ticker).history(period="2y")
        
        if not df.empty:
            df = df.reset_index()
            # Clean and localize timezone-aware Date column
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
                
                # If run on weekend (Saturday=5, Sunday=6), filter data to end on Friday
                import datetime
                today = datetime.date.today()
                weekday = today.weekday()
                if weekday == 5: # Saturday
                    friday = today - datetime.timedelta(days=1)
                    df = df[df['Date'].dt.date <= friday]
                elif weekday == 6: # Sunday
                    friday = today - datetime.timedelta(days=2)
                    df = df[df['Date'].dt.date <= friday]
                
                # Compute indicators and return summary metrics
                metrics = compute_latest_metrics(df)
                if metrics and len(df) > 0:
                    metrics['ticker'] = ticker
                    latest_date = df['Date'].iloc[-1].strftime('%Y-%m-%d')
                    return metrics, latest_date, f"Successfully calculated metrics for {ticker} ({len(df)} rows)"
                else:
                    return None, None, f"Warning: Could not calculate metrics for {ticker} (insufficient historical data)"
            else:
                return None, None, f"Warning: 'Date' column not found in downloaded data for {ticker}"
        else:
            return None, None, f"Warning: Downloaded empty dataframe for {ticker}"
    except Exception as e:
        return None, None, f"Error fetching data for {ticker}: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Fetch Stock Tickers in Batches & Parallel Threads")
    parser.add_argument("--batch-index", type=int, default=0, help="Zero-based index of the batch to run")
    parser.add_argument("--total-batches", type=int, default=1, help="Total number of batches the list is split into")
    parser.add_argument("--threads", type=int, default=15, help="Number of concurrent downloader threads")
    args = parser.parse_args()

    tickers = get_tickers()
    total_tickers = len(tickers)
    
    # Calculate batch chunk boundaries
    chunk_size = (total_tickers + args.total_batches - 1) // args.total_batches
    start_idx = args.batch_index * chunk_size
    end_idx = min(start_idx + chunk_size, total_tickers)
    
    if start_idx >= total_tickers:
        print(f"Error: Batch index {args.batch_index} is out of bounds (total tickers: {total_tickers}).")
        return
        
    batch_tickers = tickers[start_idx:end_idx]
    print(f"Batch {args.batch_index}/{args.total_batches}: Fetching {len(batch_tickers)} tickers out of {total_tickers} (indices {start_idx} to {end_idx-1})")
    
    summary_results = []
    latest_dates = []
    
    # Run downloads in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_ticker = {executor.submit(fetch_single_ticker, ticker): ticker for ticker in batch_tickers}
        
        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                metrics, date_str, message = future.result()
                print(message)
                if metrics:
                    summary_results.append(metrics)
                if date_str:
                    latest_dates.append(date_str)
            except Exception as e:
                print(f"Execution error for {ticker}: {str(e)}")
                
    # Save the batch summary data to CSV
    if summary_results:
        from collections import Counter
        if latest_dates:
            fetch_date = Counter(latest_dates).most_common(1)[0][0]
        else:
            import datetime
            fetch_date = datetime.date.today().strftime('%Y-%m-%d')
            
        summary_df = pd.DataFrame(summary_results)
        # Ensure exact column ordering
        summary_df = summary_df[['ticker', 'close', 'velocity', 'acceleration', 'rsi']]
        summary_filename = f"batch_summary_{args.batch_index}_{fetch_date}.csv"
        summary_df.to_csv(summary_filename, index=False)
        print(f"\n--- Batch {args.batch_index} Summary saved to {summary_filename} ({len(summary_df)} tickers successfully saved) ---")
    else:
        print(f"\n--- Warning: Batch {args.batch_index} did not produce any valid summary metrics ---")

if __name__ == "__main__":
    main()
