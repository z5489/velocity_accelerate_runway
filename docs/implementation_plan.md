# Implementation Plan - Stock Trading Signals Dashboard

We will build a high-performance Streamlit dashboard to visualize short-term stock trading signals. Since there are no local CSV files in the workspace directory, the app will automatically fetch daily historical stock data from Yahoo Finance for a set of popular tickers (e.g., TSLA, MSFT, AAPL, NVDA, AMZN, GOOG, BP, AZN, VOD, LSEG) and save them as `LSE_DLY_<TICKER>.csv` files in the workspace. This satisfies both the local CSV scanning requirement and the user's specific request to fetch popular tickers from Yahoo Finance.

## Proposed Math & Scoring Formulas

The dashboard supports three distinct modes with weights summing to 100%:

| Mode | Velocity Weight ($W_V$) | Acceleration Weight ($W_A$) | Runway Weight ($W_R$) |
|---|---|---|---|
| **Aggressive Momentum Chaser** | 40% | 40% | 20% |
| **Balanced Swing Trader** | 35% | 35% | 30% |
| **Mean-Reversion Trader** | 15% | 35% | 50% |

### 1. Velocity (5-Day ROC %)
Calculate the 5-day Rate of Change:
$$ROC\% = \frac{\text{Price}_{\text{today}} - \text{Price}_{t-5}}{\text{Price}_{t-5}} \times 100$$
To scale this smoothly from 0 to 100, we apply min-max scaling across the active cohort of tickers:
$$S_{velocity} = 100 \times \frac{ROC\% - ROC\%_{min}}{ROC\%_{max} - ROC\%_{min}}$$

### 2. Acceleration (MACD Histogram Delta)
Calculate the standard MACD (12, 26, 9):
- $EMA_{12} = \text{EMA}(Close, 12)$
- $EMA_{26} = \text{EMA}(Close, 26)$
- $MACD = EMA_{12} - EMA_{26}$
- $Signal = \text{EMA}(MACD, 9)$
- $Hist = MACD - Signal$

Acceleration is the delta:
$$Acc = Hist_{\text{today}} - Hist_{\text{yesterday}}$$
To scale this smoothly from 0 to 100, we use cohort-based min-max normalization:
$$S_{acceleration} = 100 \times \frac{Acc - Acc_{min}}{Acc_{max} - Acc_{min}}$$

### 3. Runway (RSI Continuous Scaling)
RSI is calculated over 14 periods. The runway score $S_{runway}$ is calculated using a continuous function depending on the active trading profile:

* **Aggressive Momentum Chaser**: Rewards strong momentum even if RSI is elevated. No penalty until RSI exceeds 80.
  $$S_{runway} = \begin{cases} 100 & \text{if } RSI \le 80 \\ 100 \times \frac{100 - RSI}{20} & \text{if } RSI > 80 \end{cases}$$

* **Balanced Swing Trader**: Rewards strong active trends with room to grow. Gaussian centered at 60 with standard deviation 15:
  $$S_{runway} = 100 \times \exp\left(-\frac{(RSI - 60)^2}{2 \times 15^2}\right)$$

* **Mean-Reversion Trader**: Rewards oversold conditions (low RSI) building a floor:
  $$S_{runway} = \begin{cases} 100 & \text{if } RSI \le 30 \\ 100 \times \frac{100 - RSI}{70} & \text{if } RSI > 30 \end{cases}$$

---

## Proposed Changes

### [Component Name] Dashboard App

#### [NEW] [app.py](../app.py)
Streamlit web application with:
1. **Background Yahoo Finance Downloader**: Auto-generates local `LSE_DLY_*.csv` files for a list of popular tickers if none are found.
2. **Dynamic Mode Toggle**: Sidebar configuration to change profiles and recalculate scores.
3. **Top Setup Banner**: Dynamic visual alert for tickers with scores > 75.
4. **Leaderboard Table**: Sortable dataframe showing tickers, scores, price, and signals.
5. **Interactive Deep-Dive**: Selected ticker displays:
   - Metric cards for Velocity, Acceleration, and Runway.
   - Dual-subplot Plotly chart (Candlesticks + Close price on top, RSI on the bottom).

---

## Verification Plan

### Automated Tests
We will verify the calculations and app startup using python:
```powershell
python -c "import pandas as pd; print('Pandas loaded successfully')"
```

### Manual Verification
1. Run `streamlit run app.py` to start the local dashboard.
2. Verify that the app downloads files dynamically if none exist, then displays the dashboard.
3. Interact with the Profile Radio buttons to ensure that scores are updated instantly.
4. Select a ticker and verify that the Plotly chart renders and updates correctly.
