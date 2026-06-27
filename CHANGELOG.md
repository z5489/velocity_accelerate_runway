# Changelog

This document tracks all version commits and updates for the Hologram Quant Trading Signals Dashboard project.

## Current Changes (To Be Committed)

### Parallel Batch Fetching & Automation
* **Unified Universe configuration**: Extracted the default stock ticker universe to [tickers.txt](file:///tickers.txt) for simple user updates.
* **Batch Fetcher Script**: Created [fetch_data.py](file:///fetch_data.py) to support parallel batch fetching with multi-threaded downloads, indicator computing, and date-stamped summaries.
* **GitHub Actions Workflow**: Created [.github/workflows/fetch_data.yml](file:///.github/workflows/fetch_data.yml) to automate data updates. It fetches daily weekday data at 11 PM UTC in parallel and commits batch summaries back to the repository.
* **Historical Date Selector**: Added a **📅 Analysis Date** sidebar selectbox in [app.py](file:///app.py) to load historical summary states.
* **On-Demand Deep-Dive**: Refactored the dashboard deep-dive charts to query Yahoo Finance on-the-fly, aligned to the selected date.
* **Weekend Filters**: Integrated weekend filters to automatically fetch Friday close data if run on Saturdays or Sundays.
* **Workflow Dependencies Caching**: Added [requirements.txt](file:///requirements.txt) to track package requirements and configured workflow caching via `actions/setup-python` in both workflow jobs to optimize run times and prevent import errors.
* **Summary Consolidation & Output Directory**: Configured the GitHub Actions workflow to aggregate all parallel matrix batch summaries into a single consolidated `output/summary_<date>.csv` file, sorting by ticker to ensure clean, minimal diffs. Stored summaries in a dedicated `output/` folder and updated the Streamlit dashboard to load files from this folder.

---

## Previous Commits

### Clean up (Local paths & media)
* Localized walkthrough images to [docs/images/](file:///docs/images/) and replaced hardcoded absolute file links with relative paths.
* Cleaned up personal file paths from [README.md](file:///README.md) and documentation.

### cabc359 - MVP Velocity Acceleration Runway dashboard
* Created [app.py](file:///app.py) Streamlit application.
* Implemented the glassmorphic dark theme and custom Outfit fonts.
* Added metric grids, Plots subplots (Candlesticks + SMA + RSI), and profile engines (Aggressive Momentum, Balanced Swing, Mean-Reversion).

### 05fa345 - First MVP
* Initialized repository layout and configuration.
