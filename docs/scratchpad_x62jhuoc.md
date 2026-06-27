# Verification Checklist
- [x] Open http://localhost:8501 and wait for load <!-- id: 0 -->
- [x] Capture initial screenshot <!-- id: 1 -->
- [x] Verify profile selection (select 'Aggressive Momentum Chaser') <!-- id: 2 -->
- [x] Verify leaderboard updates <!-- id: 3 -->
- [x] Select another ticker in Technical Deep-Dive <!-- id: 4 -->
- [x] Verify Plotly charts render correctly <!-- id: 5 -->
- [x] Record active profile weights and top trade setup <!-- id: 6 -->
- [x] Check for visual layout errors <!-- id: 7 -->

## Findings
- **Balanced Swing Trader (Default)**:
  - Weights: Velocity 35%, Acceleration 35%, Runway 30%
  - Top Trade Setup: META (Score: 87.9/100)
- **Aggressive Momentum Chaser**:
  - Weights: Velocity 40%, Acceleration 40%, Runway 20%
  - Top Trade Setup: META (Score: 99.9/100)
- **Mean-Reversion Trader**:
  - Weights: Runway 50%, Acceleration 35%, Velocity 15%
  - Top Trade Setup: AMZN (Score: 87.5/100)
  - AMZN metrics under Mean-Reversion: Velocity 0.73% (Score: 24.5), Acceleration 0.29972 (Score: 99.9), Runway RSI 31.6 (Score: 97.6).
- **Deep-Dive view and Plotly Charts**:
  - Successfully selected TSLA and AMZN.
  - Candlestick and RSI subplot render correctly (Plotly mode bar is visible in DOM).
  - No visual layout errors detected.

