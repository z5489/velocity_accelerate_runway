# Hologram | Quant Trading Signals Dashboard

Hologram is a high-performance Streamlit dashboard designed to visualize short-term stock trading signals. It computes dynamic momentum and mean-reversion scoring across stock universes by combining customized cohort-normalized velocity, acceleration, and runway technical metrics.

---

## 🚀 Key Features

* **Dynamic Trading Profiles**: Configure calculations instantly between three strategies:
  * **Aggressive Momentum Chaser** (40% Velocity / 40% Acceleration / 20% Runway)
  * **Balanced Swing Trader** (35% Velocity / 35% Acceleration / 30% Runway)
  * **Mean-Reversion Trader** (15% Velocity / 35% Acceleration / 50% Runway)
* **Automated Universe Loading**: Scans the local directory for `LSE_DLY_*.csv` files, automatically cleans ticker strings, and auto-downloads default stock data from Yahoo Finance if none exist.
* **Continuous Mathematical Scaling**:
  * **Velocity**: Cohort-normalized 5-Day Rate of Change (ROC%).
  * **Acceleration**: Cohort-normalized MACD Histogram delta ($Hist_{today} - Hist_{yesterday}$).
  * **Runway**: Continuous RSI functions custom-tailored to reward momentum or bottom reversals.
* **Premium Glassmorphic Design**: Dark terminal aesthetics with Google Fonts ("Outfit"), custom responsive metrics, dynamic setup banners (gold/green glow for scores >75), and fully interactive Plotly Candlestick and RSI subplots.

---

## 🛠️ Installation & Setup

### 1. Clone & Navigate to Workspace
```powershell
cd c:\Users\ziyen\velocity_acceleration_runway
```

### 2. Install Required Dependencies
Ensure you have Python 3.8+ installed. Install the necessary quantitative and web UI packages:
```powershell
pip install streamlit pandas numpy plotly yfinance
```

### 3. Run the Dashboard
Start the Streamlit application:
```powershell
streamlit run app.py
```

Streamlit will boot up the local webserver. By default, it will be available at:
👉 **`http://localhost:8501`**

---

## 📐 Scoring & Mathematical Formulas

The **Total Probability Score** (0-100) is calculated as:
$$Score_{total} = W_{velocity} \cdot S_{velocity} + W_{acceleration} \cdot S_{acceleration} + W_{runway} \cdot S_{runway}$$

Where:
1. **$S_{velocity}$**: Min-max scaling of the 5-day Rate of Change ($ROC\%$) across the ticker cohort.
2. **$S_{acceleration}$**: Min-max scaling of the MACD Histogram magnitude change ($Acc$) across the ticker cohort.
3. **$S_{runway}$**: Continuous scaling function mapping the 14-day RSI value:
   * **Aggressive Momentum**: No penalty if $RSI \le 80$. Linear decay to 0 if $RSI > 80$.
   * **Balanced Swing**: Gaussian bell curve centered at RSI 60 with standard deviation 15:
     $$S_{runway} = 100 \cdot \exp\left(-\frac{(RSI - 60)^2}{2 \cdot 15^2}\right)$$
   * **Mean-Reversion**: Inverted linear decay. Maximum score of 100 if $RSI \le 30$. Linear decay to 0 for higher RSIs.
