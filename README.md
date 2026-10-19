# EquityLens AI — Institutional Equity Research Terminal

EquityLens AI is an equity research platform for Indian listed equities (NSE & BSE), combining real-time market data, interactive technical charts, institutional fundamental snapshots, and generative equity research memos powered by NVIDIA NIM (Google Gemma model).

---

## 🌟 Key Features

- **NSE & BSE Market Coverage:** Live quotes, 52-week ranges, trading volume, and market capitalisation.
- **Top-Right Search & Ticker Filter:** Instant search across top Indian large caps with support for any custom NSE (`.NS`) or BSE (`.BO`) scrip.
- **Fundamental Scorecard:** Market Cap, Trailing & Forward P/E, Return on Equity (ROE), Trailing EPS, Net Profit Margins, and 52-Week Range.
- **Interactive Candlestick & Volume Charts:** Plotly financial charts with timeframe selection (1M, 6M, 1Y, 5Y) and volume overlays.
- **AI Equity Research Analyst:** Grounded, institutional-grade 5-part research memos generated via NVIDIA NIM (`google/gemma-4-31b-it`).
- **Institutional PDF Export:** Download formatted equity research reports generated on-the-fly using ReportLab.

---

## 🚀 Deployment Guide (Streamlit Community Cloud — Recommended)

Streamlit Community Cloud is 100% free and provides a permanent public URL (e.g. `https://equitylens-ai.streamlit.app`).

### Step 1: Push Code to GitHub

```bash
git init
git add .
git commit -m "Deploy EquityLens AI Terminal"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/equitylens-ai.git
git push -u origin main
```

*(Note: `.env` is automatically excluded by `.gitignore` to protect your API keys)*

### Step 2: Deploy on Streamlit Cloud

1. Visit [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
2. Click **"New app"**.
3. Select your repository: `<YOUR_USERNAME>/equitylens-ai`.
4. Set Main file path: `app.py`.
5. Click **"Advanced settings..."** -> **"Secrets"**.
6. Paste your NVIDIA API key in the secrets editor:

```toml
NVIDIA_API_KEY = "nvapi-your-key-here"
```

7. Click **"Deploy!"**. Your application will be live in 1-2 minutes!

---

## 💻 Local Development Setup

1. **Clone & Navigate:**
   ```bash
   cd "EQYITYLENS AI"
   ```

2. **Create and Activate Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Secrets:**
   Create a `.env` file in the project root:
   ```env
   NVIDIA_API_KEY=nvapi-your-key-here
   ```

5. **Launch Terminal:**
   ```bash
   streamlit run app.py
   ```
