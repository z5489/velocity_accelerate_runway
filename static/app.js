// State
let cohortData = [];
let availableDates = [];
let activeDistributionToggle = 'sector'; // 'sector' or 'industry'

// Mode configuration
const modeConfig = {
    'Aggressive Momentum Chaser': {
        weights: { vel: 40, acc: 40, run: 20 },
        desc: 'Focusses on rapid price momentum and acceleration. Runway acts as a safety filter only penalizing overbought conditions (>80 RSI).'
    },
    'Balanced Swing Trader': {
        weights: { vel: 35, acc: 35, run: 30 },
        desc: 'Balances active medium-term trends with remaining room to run. Scores peaked near 60 RSI to avoid early entries or extreme overbought states.'
    },
    'Mean-Reversion Trader': {
        weights: { vel: 15, acc: 35, run: 50 },
        desc: 'Mean-reversion model searching for oversold stock floors (low RSI) that are actively accelerating upwards (MACD delta reversal).'
    },
    'Bearish Short': {
        weights: { vel: 35, acc: 35, run: 30 },
        desc: 'Inverse momentum model. Rewards negative velocity, decreasing MACD histograms, and overbought RSI levels (peak 70) to identify high-conviction short setups.'
    }
};

// DOM Elements
const dateSelect = document.getElementById('dateSelect');
const modeRadios = document.querySelectorAll('input[name="mode"]');
const activeModeEl = document.getElementById('activeMode');
const wVelEl = document.getElementById('wVel');
const wAccEl = document.getElementById('wAcc');
const wRunEl = document.getElementById('wRun');
const modeDescEl = document.getElementById('modeDesc');
const totalSignalsEl = document.getElementById('totalSignals');
const avgScoreEl = document.getElementById('avgScore');
const cohortTableBody = document.getElementById('cohortTableBody');
const toggleSectorBtn = document.getElementById('toggleSector');
const toggleIndustryBtn = document.getElementById('toggleIndustry');

// Fetch cohort data
async function fetchCohort() {
    const universe = 'US Stocks';
    const date = dateSelect.value;
    const mode = getSelectedMode();
    
    const params = new URLSearchParams({ universe, mode });
    if (date) params.append('date', date);
    
    try {
        const [cohortRes, topRes] = await Promise.all([
            fetch(`/api/cohort?${params}`),
            fetch(`/api/top-ticker?${params}`)
        ]);
        
        const cohortData = await cohortRes.json();
        const topData = await topRes.json();
        
        updateUI(cohortData.cohort, topData);
    } catch (err) {
        console.error('Failed to fetch cohort:', err);
    }
}

// Fetch available dates
async function fetchDates() {
    const universe = 'US Stocks';
    const params = new URLSearchParams({ universe });
    
    try {
        const res = await fetch(`/api/dates?${params}`);
        const data = await res.json();
        availableDates = data.dates;
        
        // Populate date dropdown
        dateSelect.innerHTML = '';
        if (availableDates.length > 0) {
            availableDates.forEach(date => {
                const opt = document.createElement('option');
                opt.value = date;
                opt.textContent = date;
                dateSelect.appendChild(opt);
            });
        } else {
            const opt = document.createElement('option');
            opt.value = '';
            opt.textContent = 'No dates available';
            dateSelect.appendChild(opt);
        }
    } catch (err) {
        console.error('Failed to fetch dates:', err);
    }
}

// Get selected mode
function getSelectedMode() {
    const checked = document.querySelector('input[name="mode"]:checked');
    return checked ? checked.value : 'Balanced Swing Trader';
}

// Update UI with new data
function updateUI(data, topData) {
    cohortData = data;
    
    // Update mode display
    const config = modeConfig[getSelectedMode()];
    activeModeEl.textContent = getSelectedMode();
    wVelEl.textContent = config.weights.vel + '%';
    wAccEl.textContent = config.weights.acc + '%';
    wRunEl.textContent = config.weights.run + '%';
    modeDescEl.textContent = config.desc;
    
    // Update metric cards
    if (data.length > 0) {
        // Calculate criteria: tickers with score >= 90
        const count90Plus = data.filter(d => d['Total Score'] >= 90).length;
        totalSignalsEl.textContent = `${count90Plus} / ${data.length}`;
        
        const avg = data.reduce((sum, d) => sum + d['Total Score'], 0) / data.length;
        avgScoreEl.textContent = avg.toFixed(1);
    } else {
        totalSignalsEl.textContent = '0 / 0';
        avgScoreEl.textContent = '--';
    }
    
    // Update distribution chart
    renderDistributionChart();
    
    // Update table
    updateTable(data);
    
    // Load chart for top ticker if available
    if (topData.ticker) {
        loadChart(topData.ticker);
        // Highlight row
        const row = document.querySelector(`#cohortTableBody tr[data-ticker="${topData.ticker}"]`);
        if (row) row.classList.add('selected-row');
    }
}

// Update table
function updateTable(data) {
    if (data.length === 0) {
        cohortTableBody.innerHTML = '<tr><td colspan="13" class="loading-cell">No data available</td></tr>';
        return;
    }
    
    cohortTableBody.innerHTML = data.map((item, idx) => {
        const isHighScore = item['Total Score'] >= 90;
        const rowClass = isHighScore ? 'high-score-row' : '';
        
        return `
            <tr data-ticker="${item.Ticker}" class="${rowClass}">
                <td>${idx + 1}</td>
                <td><strong>${item.Ticker}</strong></td>
                <td>${item.Name}</td>
                <td>${item.Sector}</td>
                <td>${item.Industry}</td>
                <td><strong style="color: #38bdf8;">${item['Total Score']}</strong></td>
                <td>${item['Velocity Score']}</td>
                <td>${item['Acceleration Score']}</td>
                <td>${item['Runway Score']}</td>
                <td>$${item['Close Price']}</td>
                <td>${item['5-Day ROC %']}</td>
                <td>${item['MACD Hist Delta']}</td>
                <td>${item['RSI']}</td>
            </tr>
        `;
    }).join('');
}

// Load chart for a ticker
async function loadChart(ticker) {
    try {
        const res = await fetch(`/api/chart?ticker=${encodeURIComponent(ticker)}&period=6mo`);
        const data = await res.json();
        
        if (data.error || !data.data || data.data.length === 0) {
            console.log('No chart data for', ticker);
            return;
        }
        
        renderChart(data.data);
    } catch (err) {
        console.error('Failed to load chart:', err);
    }
}

// Render Plotly chart
function renderChart(chartData) {
    const dates = chartData.map(d => d.Date);
    const opens = chartData.map(d => d.Open);
    const highs = chartData.map(d => d.High);
    const lows = chartData.map(d => d.Low);
    const closes = chartData.map(d => d.Close);
    const ma20 = chartData.map(d => d.MA20);
    const ma50 = chartData.map(d => d.MA50);
    const rsi = chartData.map(d => d.RSI);
    
    // Candlestick + MAs
    const candlestickTrace = {
        x: dates,
        open: opens,
        high: highs,
        low: lows,
        close: closes,
        type: 'candlestick',
        name: 'Candlestick',
        increasing: { line: { color: '#10b981' } },
        decreasing: { line: { color: '#ef4444' } }
    };
    
    const ma20Trace = {
        x: dates,
        y: ma20,
        type: 'scatter',
        mode: 'lines',
        name: '20-Day SMA',
        line: { color: '#0ea5e9', width: 1.5 }
    };
    
    const ma50Trace = {
        x: dates,
        y: ma50,
        type: 'scatter',
        mode: 'lines',
        name: '50-Day SMA',
        line: { color: '#a855f7', width: 1.5 }
    };
    
    // RSI
    const rsiTrace = {
        x: dates,
        y: rsi,
        type: 'scatter',
        mode: 'lines',
        name: 'RSI',
        line: { color: '#f97316', width: 2 }
    };
    
    const layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(17, 24, 39, 0.4)',
        font: { color: '#ffffff' },
        margin: { l: 55, r: 20, t: 35, b: 40 },
        showlegend: true,
        legend: {
            orientation: 'h',
            yanchor: 'bottom',
            y: 1.02,
            xanchor: 'right',
            x: 1,
            bgcolor: 'rgba(0,0,0,0)'
        },
        xaxis: {
            gridcolor: 'rgba(255,255,255,0.05)',
            showline: true,
            linecolor: 'rgba(255,255,255,0.1)',
            rangeslider: { visible: false }
        },
        yaxis: {
            gridcolor: 'rgba(255,255,255,0.05)',
            showline: true,
            linecolor: 'rgba(255,255,255,0.1)',
            title: { text: 'Price', font: { color: '#ffffff' } }
        }
    };
    
    const config = { responsive: true, displayModeBar: false };
    
    Plotly.newPlot('candlestickChart', [candlestickTrace, ma20Trace, ma50Trace], layout, config);
    
    // RSI layout
    const rsiLayout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(17, 24, 39, 0.4)',
        font: { color: '#ffffff' },
        margin: { l: 55, r: 20, t: 15, b: 40 },
        showlegend: false,
        xaxis: {
            gridcolor: 'rgba(255,255,255,0.05)',
            showline: true,
            linecolor: 'rgba(255,255,255,0.1)'
        },
        yaxis: {
            gridcolor: 'rgba(255,255,255,0.05)',
            showline: true,
            linecolor: 'rgba(255,255,255,0.1)',
            range: [0, 100],
            title: { text: 'RSI', font: { color: '#ffffff' } }
        },
        shapes: [
            {
                type: 'line', y0: 70, y1: 70, x0: 0, x1: 1,
                xref: 'x', yref: 'y',
                line: { color: '#ef4444', width: 1, dash: 'dash' }
            },
            {
                type: 'line', y0: 50, y1: 50, x0: 0, x1: 1,
                xref: 'x', yref: 'y',
                line: { color: '#4b5563', width: 0.8, dash: 'dot' }
            },
            {
                type: 'line', y0: 30, y1: 30, x0: 0, x1: 1,
                xref: 'x', yref: 'y',
                line: { color: '#10b981', width: 1, dash: 'dash' }
            }
        ]
    };
    
    Plotly.newPlot('rsiChart', [rsiTrace], rsiLayout, config);
}

// Render Pie Chart of Sector/Industry distribution for Tickers >= 90
function renderDistributionChart() {
    const container = document.getElementById('distributionChartContainer');
    
    // Exclude ETFs from distribution chart
    const highScoringTickers = cohortData.filter(d => {
        if (d['Total Score'] < 90) return false;
        const sector = (d.Sector || '').trim().toUpperCase();
        const industry = (d.Industry || '').trim().toUpperCase();
        return sector !== 'ETF' && industry !== 'ETF';
    });
    
    if (highScoringTickers.length === 0) {
        container.innerHTML = '<div class="no-data-message">No active signals with Score ≥ 90 to display distribution (excluding ETFs)</div>';
        return;
    }
    
    // Clear and restore distributionChart element
    container.innerHTML = '<div id="distributionChart"></div>';
    
    // Aggregate by active toggle
    const aggregates = {};
    highScoringTickers.forEach(item => {
        const key = activeDistributionToggle === 'sector' ? item.Sector : item.Industry;
        aggregates[key] = (aggregates[key] || 0) + 1;
    });
    
    const labels = Object.keys(aggregates);
    const values = Object.values(aggregates);
    
    const trace = {
        labels: labels,
        values: values,
        type: 'pie',
        hole: 0.4, // modern donut style
        textinfo: 'percent',
        hoverinfo: 'label+value+percent',
        textposition: 'inside',
        marker: {
            colors: ['#0ea5e9', '#10b981', '#a855f7', '#f97316', '#ef4444', '#eab308', '#6366f1', '#ec4899', '#14b8a6']
        }
    };
    
    const layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#ffffff', family: 'Outfit, sans-serif' },
        margin: { l: 20, r: 20, t: 20, b: 20 },
        showlegend: true,
        legend: {
            font: { color: '#ffffff', size: 11 },
            orientation: 'v',
            x: 1.05,
            y: 0.5,
            yanchor: 'middle'
        }
    };
    
    const config = { responsive: true, displayModeBar: false };
    Plotly.newPlot('distributionChart', [trace], layout, config);
}

// Event listeners
dateSelect.addEventListener('change', fetchCohort);

modeRadios.forEach(radio => {
    radio.addEventListener('change', fetchCohort);
});

cohortTableBody.addEventListener('click', (e) => {
    const row = e.target.closest('tr');
    if (!row) return;
    
    const ticker = row.dataset.ticker;
    if (ticker) {
        // Highlight selected row
        document.querySelectorAll('#cohortTableBody tr').forEach(r => r.classList.remove('selected-row'));
        row.classList.add('selected-row');
        
        // Load chart
        loadChart(ticker);
    }
});

// Toggle sector/industry pie chart
toggleSectorBtn.addEventListener('click', () => {
    if (activeDistributionToggle !== 'sector') {
        activeDistributionToggle = 'sector';
        toggleSectorBtn.classList.add('active');
        toggleIndustryBtn.classList.remove('active');
        renderDistributionChart();
    }
});

toggleIndustryBtn.addEventListener('click', () => {
    if (activeDistributionToggle !== 'industry') {
        activeDistributionToggle = 'industry';
        toggleIndustryBtn.classList.add('active');
        toggleSectorBtn.classList.remove('active');
        renderDistributionChart();
    }
});

// Initial load
fetchDates().then(fetchCohort);