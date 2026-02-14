Multi-Indicator Asset Screener

Systematic Signal Engine for Quantitative Strategy Research

Quick start:

git clone https://github.com/The-Pranay-Pandey/asset-screener.git
cd asset-screener
pip install -r requirements.txt
python screener.py


1. Executive Summary

The Multi-Indicator Asset Screener is a modular technical signal engine designed for systematic trading research.

It programmatically computes multiple trend, momentum, and volatility indicators and standardizes their outputs into a structured signal matrix suitable for:

Quantitative research

Multi-factor strategy development

Signal stacking

Feature engineering for ML models

Regime detection

Multi-timeframe systems

The system is built with extensibility, computational efficiency, and research clarity in mind.


2. System Architecture

The screener follows a layered architecture:

Data Layer  →  Indicator Engine  →  Signal Normalization  →  Export Layer

2.1 Data Layer

Downloads OHLC data via yfinance

Cleans missing values

Adjusts timezone (UTC → IST)

Prepares asset-specific DataFrames

2.2 Indicator Engine

Each indicator is computed independently and vectorized using pandas operations for efficiency.

2.3 Signal Normalization

All outputs are standardized:

Value	Meaning
1	    Bullish
-1	    Bearish
0	    Neutral
Text	Regime classification (ADX)

This normalization enables:

Weighted signal aggregation

Ensemble construction

Backtesting integration

2.4 Output Layer

Signals are exported to:

signals_output.csv


With a MultiIndex structure:

Level 1 → Ticker
Level 2 → Indicator


This design allows cross-sectional and time-series analysis without structural modification.

3. Indicators Implemented

| Indicator             | Category       | Research Purpose                |
| --------------------- | -------------- | ------------------------------- |
| SMA Crossover         | Trend          | Baseline trend filter           |
| EMA Crossover         | Trend          | Faster trend detection          |
| RSI                   | Momentum       | Overbought / Oversold detection |
| MACD                  | Momentum       | Momentum regime shift           |
| Bollinger Bands       | Volatility     | Mean reversion triggers         |
| Stochastic Oscillator | Momentum       | Entry timing                    |
| ADX                   | Trend Strength | Regime classification           |

4. Quantitative Design Principles

4.1 Modularity

Indicators are controlled via a configuration dictionary:

actions = {
    'sma':[20,10],
    'ema':[20,10],
    'rsi':14,
    'macd':[26,12,9],
    'bollinger_bands':[20,2],
    'stochastic':12,
    'adx':14
}


This allows:

Parameter optimization

Walk-forward testing

Indicator toggling

Rapid research iteration

4.2 Vectorization

All calculations use vectorized operations:

.rolling()

.ewm()

np.where()

This ensures:

O(N) time complexity

Scalability across assets

Suitability for portfolio-level screening

4.3 Regime Awareness (ADX Classification)

ADX is categorized into regimes:

ADX Range	Interpretation
< 20	Sideways
20–25	Developing Trend
25–50	Strong Trend
50–75	Extremely Strong
75–100	Near Exhaustion

This allows strategy conditioning:

Apply mean reversion in low ADX regimes

Apply trend-following in high ADX regimes

5. Example Research Workflow

Example: Multi-Timeframe Trend System

Higher Timeframe (1H):

EMA crossover confirms trend

ADX > 25 confirms regime strength

Lower Timeframe (5M):

RSI < 30 triggers pullback entry

Stochastic crossover confirms timing

This framework supports professional systematic logic:

Trend alignment + Momentum timing + Regime filtering

6. Output Use Cases

The signal matrix can be used for:

Composite signal scoring

Majority-vote systems

Indicator weighting models

Feature engineering for ML pipelines

Strategy performance benchmarking

Risk model conditioning

7. Risk & Data Considerations

Yahoo Finance intraday data has limited depth

Indicator warm-up periods may distort early values

ADX smoothing may produce elevated initial readings

No transaction cost modeling included

This engine is intended for research, not direct live deployment.

8. Future Institutional Extensions

ATR-based volatility normalization

Position sizing module

Signal weighting optimizer

Walk-forward testing framework

Performance analytics dashboard

Multi-asset cross-sectional ranking

Database storage layer (SQL integration)

Parallelized processing (for portfolio-scale screening)

9. Installation
pip install yfinance pandas numpy

10. Strategic Positioning

This project demonstrates:

Understanding of systematic trading structure

Indicator mathematics implementation

Signal normalization principles

Modular research design

Portfolio-ready architecture

It is structured as a foundation for:

Multi-factor systems

Trend-following frameworks

Mean reversion overlays

Hybrid discretionary-systematic workflows

## Disclaimer

This project is intended for research and educational purposes only.  
It does not constitute investment advice and is not production-ready trading software.

