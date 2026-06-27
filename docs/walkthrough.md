# Walkthrough - Quant Trading Signals Dashboard (Hologram)

We have successfully built and verified the high-performance Streamlit dashboard, **Hologram**, located at [app.py](file:///c:/Users/ziyen/velocity_acceleration_runway/app.py).

The application is completely self-contained. Since the workspace started empty, the app automatically downloads historical daily data for a set of popular tickers (US: TSLA, MSFT, AAPL, NVDA, AMZN, GOOGL, META; UK: BP.L, AZN.L, VOD.L, LSEG.L) from Yahoo Finance, saves them as local `LSE_DLY_<TICKER>.csv` files, parses them, and computes high-fidelity quantitative indicators.

---

## 📈 Visual Walkthrough & UI Design

Below is a carousel showcasing the UI/UX design, active strategy configs, cohort leaderboards, custom metric cards, and interactive Plotly subplots.

````carousel
![Hologram Dashboard - Initial Load (Balanced Swing Trader)](/C:/Users/ziyen/.gemini/antigravity-ide/brain/3ba536ca-0873-49c9-b971-a5ff75763aff/initial_load_1782516932621.png)
<!-- slide -->
![Aggressive Momentum Profile Selected - Recomputed Rankings](/C:/Users/ziyen/.gemini/antigravity-ide/brain/3ba536ca-0873-49c9-b971-a5ff75763aff/aggressive_momentum_1782516955594.png)
<!-- slide -->
![TSLA Deep-Dive Panel and Custom Metrics](/C:/Users/ziyen/.gemini/antigravity-ide/brain/3ba536ca-0873-49c9-b971-a5ff75763aff/tsla_deep_dive_1782516974369.png)
<!-- slide -->
![Interactive Candlestick and RSI Subplots](/C:/Users/ziyen/.gemini/antigravity-ide/brain/3ba536ca-0873-49c9-b971-a5ff75763aff/tsla_charts_1782516983702.png)
<!-- slide -->
![Mean Reversion Profile - Low RSI Scoring Inverse Functions](/C:/Users/ziyen/.gemini/antigravity-ide/brain/3ba536ca-0873-49c9-b971-a5ff75763aff/mean_reversion_1782517002416.png)
````

### 🎥 Verification Recording
The complete interactive browser verification recording showing the strategy transitions, data re-sorting, and deep dive charts rendering can be viewed below:

![Browser verification of trading dashboard](/C:/Users/ziyen/.gemini/antigravity-ide/brain/3ba536ca-0873-49c9-b971-a5ff75763aff/dashboard_ui_verification_1782516909190.webp)

---

## 🛠️ Summary of Implemented Features

### 1. Data Ingestion & Cleaner
- Automatically scans the directory for files matching `LSE_DLY_*.csv`.
- Cleans ticker strings dynamically (e.g., `LSE_DLY_BP.L, 1D (2).csv` is cleaned to `BP.L`).
- **Auto-Bootstrapping**: If no CSVs are found locally, the app automatically fetches daily data for a popular universe using the `yfinance` API. If offline, it uses a random-walk generator as a safe fallback.

### 2. Math Signal Calculations & Normalization
- **Velocity (5-Day ROC%)**: Calculates the 5-day Rate of Change. Normalizes the values dynamically using min-max scaling across the active cohort so the top performer receives a score of 100.
- **Acceleration (MACD Histogram Delta)**: Computes the 12/26/9 MACD histogram and calculates the difference between today's histogram bar and yesterday's bar. Normalizes this delta across the cohort so the strongest accelerating asset receives 100.
- **Runway (RSI Continuous Scaling)**: Uses strategy-specific mathematical scaling functions mapping the 14-Day RSI values:
  - *Momentum Chaser*: Score of 100 if RSI $\le$ 80; tapers linearly to 0 from 80 to 100.
  - *Balanced Swing*: Gaussian function centered at 60 with standard deviation 15, yielding peaks near active trend zones.
  - *Mean-Reversion*: Inverted linear scale giving a score of 100 if RSI $\le$ 30; tapers linearly to 0 from 30 to 100.

### 3. Sleek UI/UX & Layout
- **Glassmorphic Theme**: Dark gradient background (`#111827` to `#030712`) styled with modern google typography (`Outfit`).
- **Profile Weights Indicator**: Header card showing current strategy config weights and description.
- **Glowing Setup Banner**: Alerts users when a ticker clears the 75/100 threshold score (e.g., `META` scoring 99.9/100 under Aggressive Momentum).
- **Interactive Leaderboard Table**: Sortable dataframe displaying indicators, scores, and raw metrics.
- **Technical Deep-Dive**: Selected ticker displays three high-fidelity metric cards alongside interactive dual-subplot Plotly charts (Candlesticks + SMAs on top, RSI on bottom).
