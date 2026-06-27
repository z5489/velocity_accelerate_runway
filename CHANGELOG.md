# Changelog

This document tracks all version commits and updates for the Hologram Quant Trading Signals Dashboard project.

## Current Changes (To Be Committed)

### Feature Additions & Multi-Universe Support
* **UK ETFs Universe**: Configured a new list of highly liquid UK ETF tickers in `uk_etfs.txt`.
* **Multi-Universe Selector**: Added a "Select Ticker Universe" dropdown to the sidebar in [app.py](file:///app.py) allowing users to switch dynamically between "US Stocks" and "UK ETFs".
* **Output Consolidator**: Created [consolidate.py](file:///consolidate.py) to aggregate parallel batch files grouped by date and universe suffix.
* **GitHub Actions Multi-Universe Pipeline**: Configured [.github/workflows/fetch_data.yml](file:///.github/workflows/fetch_data.yml) to fetch both universes in parallel and consolidate them separately into `output/summary_{date}.csv` and `output/summary_uk_etfs_{date}.csv`.
* **Inline Comments Support**: Updated the ticker list parser to strip inline comments so tickers can be annotated in place.
* **Metadata & Region Tracking**: Integrated `region` (US or UK), `name` (company/fund name), `sector`, and `industry` columns to the daily scraper, consolidator, and dashboard leaderboard table.
* **Cleaned Up Obsolete Fallbacks**: Deleted individual `LSE_DLY_*.csv` file generation, fallbacks, local download, and mocking logic from [app.py](file:///app.py) to rely purely on the automated daily consolidated summaries.

---

## Previous Commits

### abfec57 - Randomly select from all tied top-score tickers instead of always picking first
* Added random selection from all tied top-score tickers to prevent alphabetical bias in the banner and deep-dive selectbox.

### d4dab08 - Switch scoring from relative cohort scaling to fixed absolute thresholds
* Replaced relative min/max cohort scaling with fixed absolute metrics: a 5% 5-day ROC yields 100 on velocity, and a positive MACD hist delta yields 100 on acceleration.

### 7c65cea - Update dashboard text colors and headings to high-contrast white for readability
* Changed all grey-colored text and gradients in headers, subtext, metrics, indicator badges, and the main title to high-contrast solid white.

### 8a7c7a6 - Fix Plotly rendering NaN coordinate bug in candlestick chart
* Calculated moving averages first and dropped initial NaN rows before passing to Plotly, resolving SVG path rendering issues in the browser.

### d2242dd - Update stock data CSVs and summaries (Daily Automatic Fetch)
* Daily automated weekday run fetching closing price data and updating summaries.

### cabc359 - MVP Velocity Acceleration Runway dashboard
* Created [app.py](file:///app.py) Streamlit application.
* Implemented the glassmorphic dark theme and custom Outfit fonts.
* Added metric grids, Plots subplots (Candlesticks + SMA + RSI), and profile engines (Aggressive Momentum, Balanced Swing, Mean-Reversion).
