# Changelog

This document tracks all version commits and updates for the Hologram Quant Trading Signals Dashboard project.

## Current Changes (To Be Committed)

### Bug Fixes
* **Plotly SVG Path NaN Fix**: Resolved a rendering bug where the technical deep-dive chart would fail to display (remaining completely blank) and trigger browser SVG `NaN` path coordinate console errors. This was caused by initial `NaN` values from the rolling SMA averages (`MA20` and `MA50`) passing to Plotly's rendering engine. Moving averages are now computed first and all leading rows containing `NaN` values are dropped before rendering the candlestick and indicator traces.
* **High Contrast Text Overrides**: Changed all grey-colored text (e.g. `#94a3b8`, `#9ca3af`, `#cbd5e1`) and background-clipped text gradients in headers, subtext, metrics, indicator badges, and the main title to high-contrast solid white (`#ffffff`). Added explicit white text CSS rules targeting markdown paragraphs, headers, list items, and custom indicator modules to guarantee clean readability against dark dashboard backgrounds.

---

## Previous Commits

### d2242dd - Update stock data CSVs and summaries (Daily Automatic Fetch)
* Daily automated weekday run fetching closing price data and updating summaries.

### baa6e96 - Install dependencies in commit-and-push workflow job to fix pandas module error
* Configured workflow step python environment setup and requirement installation to prevent module error.

### 535fcdb - Aggregated old root batch summaries into output/summary_2026-06-26.csv and removed original files
* Combined parallel chunk files into a single alphabetical aggregated summary and deleted root files.

### cad7a88 - Add ability to batch fetch data
* Extracted stock universe list to `tickers.txt` and built `fetch_data.py` to support matrix parallel batch chunks.
* Configured `.github/workflows/fetch_data.yml` to automate daily fetching.
* Swapped sidebar controls to support loading historical date summaries and pulling deep-dive details dynamically on-demand.

### cabc359 - MVP Velocity Acceleration Runway dashboard
* Created [app.py](file:///app.py) Streamlit application.
* Implemented the glassmorphic dark theme and custom Outfit fonts.
* Added metric grids, Plots subplots (Candlesticks + SMA + RSI), and profile engines (Aggressive Momentum, Balanced Swing, Mean-Reversion).

### 05fa345 - First MVP
* Initialized repository layout and configuration.
