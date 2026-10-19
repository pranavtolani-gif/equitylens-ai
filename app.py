"""
EquityLens AI - Institutional Financial Research Terminal & AI Analyst
"""

import os
import json
import io
import re
from datetime import datetime
import requests
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from dotenv import load_dotenv

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

# Load local environment variables from .env file
load_dotenv(override=True)

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="EquityLens AI | Institutional Research Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Dark Financial-Terminal Styling
st.markdown("""
<style>
    /* Google Inter font import */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Base Canvas */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #0a0d14 !important;
        color: #f8fafc !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    /* Streamlit Main Content Padding - Full Screen Terminal Width */
    .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 3rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1520px !important;
    }

    /* Completely Hide Sidebar and Sidebar Toggles */
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    section[data-testid="stSidebar"],
    button[data-testid="stSidebarCollapseButton"],
    div[data-testid="stSidebarHeader"] {
        display: none !important;
        width: 0 !important;
        visibility: hidden !important;
    }

    /* Masthead Container Border Styling */
    div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type {
        background-color: #121620 !important;
        border: 1px solid #1e2433 !important;
        border-radius: 6px !important;
        margin-bottom: 20px !important;
        padding: 6px 14px !important;
    }

    /* Clean Streamlit Headers & Menus */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Dividers */
    hr {
        border-color: #1e2433 !important;
        margin: 24px 0 !important;
    }

    /* Section A: Masthead Header */
    .masthead-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #121620;
        border: 1px solid #1e2433;
        border-radius: 6px;
        padding: 14px 20px;
        margin-bottom: 20px;
    }
    .masthead-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .masthead-logo {
        width: 36px;
        height: 36px;
        background: #182030;
        border: 1px solid #232e42;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #38bdf8;
        font-size: 1.2rem;
    }
    .masthead-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: -0.01em;
        line-height: 1.2;
    }
    .masthead-subtitle {
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 500;
    }
    .masthead-right {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: rgba(16, 185, 129, 0.12);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .masthead-timestamp {
        font-size: 0.75rem;
        color: #64748b;
        font-feature-settings: 'tnum' 1;
    }

    /* Section B: Company Identity & Price */
    .company-banner {
        background-color: #121620;
        border: 1px solid #1e2433;
        border-radius: 6px;
        padding: 20px 24px;
        margin-bottom: 24px;
    }
    .eyebrow-label {
        font-size: 0.7rem;
        color: #38bdf8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
    }
    .company-title {
        font-size: 1.85rem;
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: -0.02em;
        line-height: 1.2;
        margin: 0 0 10px 0;
    }
    .tag-badge {
        display: inline-flex;
        align-items: center;
        background-color: #182030;
        color: #cbd5e1;
        border: 1px solid #1e293b;
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-right: 8px;
        margin-bottom: 4px;
    }
    .price-value {
        font-size: 2.1rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.1;
        font-feature-settings: "tnum" 1;
        margin-bottom: 6px;
    }
    .price-delta-positive {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 0.85rem;
        font-weight: 600;
        font-feature-settings: "tnum" 1;
    }
    .price-delta-negative {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background-color: rgba(244, 63, 94, 0.15);
        color: #f43f5e;
        border: 1px solid rgba(244, 63, 94, 0.35);
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 0.85rem;
        font-weight: 600;
        font-feature-settings: "tnum" 1;
    }
    .price-meta {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 6px;
    }

    /* Section Headings */
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: -0.01em;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Section C: Fundamental Metric Cards */
    .metric-card {
        background-color: #121620;
        border: 1px solid #1e2433;
        border-radius: 6px;
        padding: 14px 16px;
        min-height: 104px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-label {
        font-size: 0.68rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.35rem;
        font-weight: 700;
        color: #f8fafc;
        font-feature-settings: "tnum" 1;
        line-height: 1.2;
    }
    .metric-sub {
        font-size: 0.7rem;
        color: #64748b;
        margin-top: 4px;
    }

    /* Section D: Chart Controls */
    .chart-controls-panel {
        background-color: #121620;
        border: 1px solid #1e2433;
        border-radius: 6px;
        padding: 18px 16px;
        height: 100%;
    }
    .control-label {
        font-size: 0.72rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 8px;
    }

    /* Section E: Profile Card */
    .profile-card {
        background-color: #121620;
        border: 1px solid #1e2433;
        border-radius: 6px;
        padding: 20px 24px;
        margin-bottom: 24px;
    }
    .profile-meta-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 12px;
        margin-bottom: 16px;
        padding-bottom: 14px;
        border-bottom: 1px solid #1e2433;
    }
    .profile-meta-item {
        font-size: 0.75rem;
        color: #94a3b8;
    }
    .profile-meta-val {
        color: #f8fafc;
        font-weight: 600;
        margin-top: 2px;
    }
    .profile-text {
        font-size: 0.88rem;
        color: #cbd5e1;
        line-height: 1.65;
    }

    /* Section F: AI Research Card */
    .ai-card {
        background-color: #121620;
        border: 1px solid #1e2433;
        border-top: 3px solid #38bdf8;
        border-radius: 6px;
        padding: 22px 26px;
        margin-top: 18px;
        margin-bottom: 24px;
    }
    .ai-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 14px;
        border-bottom: 1px solid #1e2433;
        margin-bottom: 18px;
    }
    .ai-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .ai-model-badge {
        background-color: #182030;
        color: #38bdf8;
        border: 1px solid #1e293b;
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
    }

    /* Streamlit Widget Styling (Dark Terminal Polish) */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stRadio"] label,
    div[data-testid="stTextInput"] label {
        color: #94a3b8 !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #121620 !important;
        border-color: #1e2433 !important;
        color: #f8fafc !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="input"] > div {
        background-color: #121620 !important;
        border-color: #1e2433 !important;
        color: #f8fafc !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="input"] input {
        color: #f8fafc !important;
    }
    div[role="radiogroup"] label span {
        color: #cbd5e1 !important;
        font-size: 0.85rem !important;
    }

    /* Buttons */
    div.stButton > button:first-child {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        border: 1px solid #0369a1 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
        transition: all 0.15s ease-in-out !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #0369a1 !important;
        border-color: #38bdf8 !important;
        color: #ffffff !important;
    }
    div.stDownloadButton > button:first-child {
        background-color: #182030 !important;
        color: #38bdf8 !important;
        border: 1px solid #1e293b !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
        transition: all 0.15s ease-in-out !important;
    }
    div.stDownloadButton > button:first-child:hover {
        background-color: #1e293b !important;
        border-color: #38bdf8 !important;
        color: #ffffff !important;
    }

    /* Expander Styling */
    div[data-testid="stExpander"] {
        background-color: #121620 !important;
        border: 1px solid #1e2433 !important;
        border-radius: 6px !important;
    }
    div[data-testid="stExpander"] details summary {
        color: #f8fafc !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Formatting Utilities
# ---------------------------------------------------------
def format_inr(val):
    """Formats large financial figures in Indian denomination (Lakh Cr, Cr, or standard)."""
    if val is None or pd.isna(val):
        return "N/A"
    try:
        num = float(val)
        if abs(num) >= 1e12:
            return f"₹{num / 1e12:.2f} Lakh Cr"
        elif abs(num) >= 1e7:
            return f"₹{num / 1e7:.2f} Cr"
        elif abs(num) >= 1e5:
            return f"₹{num / 1e5:.2f} Lakh"
        else:
            return f"₹{num:,.2f}"
    except (ValueError, TypeError):
        return "N/A"

def format_percent(val):
    if val is None or pd.isna(val):
        return "N/A"
    try:
        num = float(val)
        return f"{num * 100:.2f}%"
    except (ValueError, TypeError):
        return "N/A"

def format_ratio(val):
    if val is None or pd.isna(val):
        return "N/A"
    try:
        num = float(val)
        return f"{num:.2f}x"
    except (ValueError, TypeError):
        return "N/A"

# ---------------------------------------------------------
# Data Fetching with Caching
# ---------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def get_company_data(symbol):
    """Fetches company profile and fundamental ratios with resilient fallback layers."""
    t = yf.Ticker(symbol)
    info = None
    try:
        raw_info = t.info
        if raw_info and isinstance(raw_info, dict):
            info = dict(raw_info)
    except Exception:
        info = None

    # Check if price is present; if not, attempt fast_info fallback
    if not info or (info.get("regularMarketPrice") is None and info.get("currentPrice") is None):
        try:
            if hasattr(t, "fast_info") and t.fast_info is not None:
                fi = t.fast_info
                info = info if info else {}
                if hasattr(fi, "last_price") and fi.last_price is not None:
                    info["currentPrice"] = float(fi.last_price)
                if hasattr(fi, "market_cap") and fi.market_cap is not None:
                    info["marketCap"] = float(fi.market_cap)
                if hasattr(fi, "previous_close") and fi.previous_close is not None:
                    info["previousClose"] = float(fi.previous_close)
                if hasattr(fi, "year_high") and fi.year_high is not None:
                    info["fiftyTwoWeekHigh"] = float(fi.year_high)
                if hasattr(fi, "year_low") and fi.year_low is not None:
                    info["fiftyTwoWeekLow"] = float(fi.year_low)
                if hasattr(fi, "currency") and fi.currency is not None:
                    info["currency"] = str(fi.currency)
        except Exception:
            pass

    # Secondary fallback: retrieve recent historical prices for current and previous close
    if not info or (info.get("regularMarketPrice") is None and info.get("currentPrice") is None):
        try:
            df = t.history(period="5d")
            if df is not None and not df.empty:
                info = info if info else {}
                info["currentPrice"] = float(df["Close"].iloc[-1])
                if len(df) > 1:
                    info["previousClose"] = float(df["Close"].iloc[-2])
        except Exception:
            pass

    if info and (info.get("currentPrice") is not None or info.get("regularMarketPrice") is not None):
        return info
    return None

@st.cache_data(ttl=300, show_spinner=False)
def get_historical_prices(symbol, period):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period=period)
        if df is not None and not df.empty:
            return df
        return None
    except Exception:
        return None

# ---------------------------------------------------------
# AI Analysis Function (NVIDIA Gemma Hosted API)
# ---------------------------------------------------------
NVIDIA_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_GEMMA_MODEL = "google/gemma-4-31b-it"

def get_nvidia_api_key():
    """Retrieves NVIDIA API key from local .env or Streamlit Cloud Secrets."""
    key = os.getenv("NVIDIA_API_KEY")
    if key:
        return key.strip()
    try:
        if hasattr(st, "secrets") and "NVIDIA_API_KEY" in st.secrets:
            return str(st.secrets["NVIDIA_API_KEY"]).strip()
    except Exception:
        pass
    return None

def generate_ai_research_memo(company_name, symbol, info, df_hist):
    """Calls NVIDIA hosted Gemma endpoint with verified financial figures to produce research memo."""
    api_key = get_nvidia_api_key()
    if not api_key:
        return None, "Backend configuration: NVIDIA_API_KEY is not configured in backend environment or cloud secrets."

    try:
        # Calculate 1-Year historical return if history available
        hist_performance_note = "Historical performance: Not available"
        if df_hist is not None and not df_hist.empty and len(df_hist) > 1:
            start_p = df_hist['Close'].iloc[0]
            end_p = df_hist['Close'].iloc[-1]
            ret_pct = ((end_p - start_p) / start_p) * 100
            hist_performance_note = (
                f"1-Year Price Trend: Started at ₹{start_p:.2f}, latest price ₹{end_p:.2f} "
                f"({ret_pct:+.2f}% over the past year)"
            )

        # Assemble real, verified fundamentals
        verified_data_block = f"""
        Company Name: {company_name}
        Ticker Symbol: {symbol}
        Exchange: National Stock Exchange of India (NSE) / BSE
        Sector: {info.get('sector', 'N/A')}
        Industry: {info.get('industry', 'N/A')}
        Current Market Price: {format_inr(info.get('currentPrice') or info.get('regularMarketPrice'))}
        Market Capitalization: {format_inr(info.get('marketCap'))}
        Trailing P/E Ratio: {format_ratio(info.get('trailingPE'))}
        Forward P/E Ratio: {format_ratio(info.get('forwardPE'))}
        Return on Equity (ROE): {format_percent(info.get('returnOnEquity'))}
        Trailing Earnings Per Share (EPS): {format_inr(info.get('trailingEps'))}
        Net Profit Margin: {format_percent(info.get('profitMargins'))}
        52-Week Range: ₹{info.get('fiftyTwoWeekLow', 0):,.2f} - ₹{info.get('fiftyTwoWeekHigh', 0):,.2f}
        Total Revenue: {format_inr(info.get('totalRevenue'))}
        {hist_performance_note}
        Business Summary: {info.get('longBusinessSummary', 'N/A')[:1200]}
        """

        prompt = f"""
You are an institutional equity research analyst specializing in the Indian stock market (NSE/BSE).
Analyze the company using the verified financial data provided below.

CRITICAL INSTRUCTIONS:
1. Ground your analysis strictly on the provided financial metrics and established business reality.
2. NEVER invent, hallucinate, or alter financial numbers. If a metric is marked 'N/A', clearly state that it is not reported.
3. Structure your equity research memo in clean GitHub-flavored markdown with the following five sections:
4. Deliver a concise, dense institutional analysis in approximately 350-450 words. Avoid unnecessary repetition.

### 1. Executive Summary & Business Operations
Brief overview of what the company does, its position in the Indian market, and primary revenue drivers.

### 2. Fundamental & Valuation Analysis
In-depth evaluation of the valuation multiples (P/E, Forward P/E) in relation to profitability (ROE, Net Profit Margins, and EPS). Explain what these ratios indicate to an investor.

### 3. Growth Catalysts & Expansion Opportunities
Key domestic or global industry trends, government initiatives in India (e.g., PLI, capex cycle, digital transformation), or market opportunities that could drive future revenue.

### 4. Key Investment Risks & Downside Factors
Significant risks including regulatory changes, input cost inflation, competitive intensity, or sector-specific headwinds.

### 5. Research Analyst Verdict
A concise synthesis summarizing the overall investment profile (e.g. Quality Compounder, Value Play, Cyclical Recovery, High Valuation Risk) based purely on the fundamentals.

VERIFIED COMPANY DATA:
{verified_data_block}
"""
        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Accept": "text/event-stream"
        }

        payload = {
            "model": NVIDIA_GEMMA_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional equity research analyst specializing in Indian listed equities on the NSE/BSE. Ground your analysis strictly on verified metrics. Never fabricate numbers. Deliver concise, high-density analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 1200,
            "stream": True
        }

        response = requests.post(
            NVIDIA_ENDPOINT,
            headers=headers,
            json=payload,
            stream=True,
            timeout=180
        )

        if response.status_code == 401:
            return None, "Authentication Error (401): The API key in .env was not accepted. Please verify your key at build.nvidia.com."
        elif response.status_code == 429:
            return None, "Rate Limit Exceeded (429): API rate limit reached. Please wait a moment before trying again."
        elif response.status_code != 200:
            return None, f"API status {response.status_code}: Unable to generate memo."

        collected_content = []
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith('data: '):
                    raw = decoded[6:].strip()
                    if raw == '[DONE]':
                        break
                    try:
                        chunk = json.loads(raw)
                        delta = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
                        if delta:
                            collected_content.append(delta)
                    except Exception:
                        pass

        full_text = ''.join(collected_content).strip()
        if full_text:
            return full_text, None
        else:
            return None, "Request completed but returned empty text. Please try again."

    except requests.exceptions.Timeout:
        return None, "request timed out. Please try again."
    except requests.exceptions.RequestException as req_err:
        return None, f"Network connection error: {req_err}"
    except Exception as e:
        return None, f"Unexpected error during research memo generation: {e}"

# ---------------------------------------------------------
# PDF Report Generator (Institutional ReportLab Engine)
# ---------------------------------------------------------
def generate_pdf_report(company_name, symbol, sector, industry, price_str, metrics_dict, memo_text, timestamp):
    """Generates an institutional PDF equity research report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0d233a'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#555555'),
        spaceAfter=10
    )
    section_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor('#1976d2'),
        spaceBefore=10,
        spaceAfter=5
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor('#222222'),
        spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#222222'),
        leftIndent=15,
        spaceAfter=4
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#777777'),
        spaceBefore=12
    )

    story = []

    # Title & Subtitle Header
    story.append(Paragraph('EquityLens AI — Equity Research Report', title_style))
    story.append(Paragraph(f'<b>Target:</b> {company_name} ({symbol}) &nbsp;|&nbsp; <b>Sector:</b> {sector} &nbsp;|&nbsp; <b>Industry:</b> {industry}<br/><b>Report Timestamp:</b> {timestamp}', subtitle_style))
    story.append(HRFlowable(width='100%', thickness=1.5, color=colors.HexColor('#0d233a'), spaceBefore=2, spaceAfter=10))

    # Fundamental Snapshot Table
    story.append(Paragraph('1. Fundamental Snapshot', section_heading))
    table_data = [
        [
            Paragraph('<b>Current Price</b>', body_style), Paragraph(price_str.replace('₹', 'Rs. '), body_style),
            Paragraph('<b>Market Cap</b>', body_style), Paragraph(metrics_dict.get('Market Cap', 'N/A').replace('₹', 'Rs. '), body_style)
        ],
        [
            Paragraph('<b>Trailing P/E</b>', body_style), Paragraph(metrics_dict.get('Trailing P/E', 'N/A'), body_style),
            Paragraph('<b>Forward P/E</b>', body_style), Paragraph(metrics_dict.get('Forward P/E', 'N/A'), body_style)
        ],
        [
            Paragraph('<b>ROE</b>', body_style), Paragraph(metrics_dict.get('ROE', 'N/A'), body_style),
            Paragraph('<b>Trailing EPS</b>', body_style), Paragraph(metrics_dict.get('Trailing EPS', 'N/A').replace('₹', 'Rs. '), body_style)
        ],
        [
            Paragraph('<b>Net Margin</b>', body_style), Paragraph(metrics_dict.get('Net Margin', 'N/A'), body_style),
            Paragraph('<b>52-Week Range</b>', body_style), Paragraph(metrics_dict.get('52-Week Range', 'N/A').replace('₹', 'Rs. '), body_style)
        ]
    ]
    t = Table(table_data, colWidths=[110, 150, 110, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d0d7de')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Research Memo Parsing
    story.append(Paragraph('2. Institutional Research Memo', section_heading))
    clean_memo = memo_text.replace('₹', 'Rs. ')
    for line in clean_memo.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('### '):
            heading_text = line.replace('### ', '').strip()
            story.append(Paragraph(heading_text, section_heading))
        elif line.startswith('## '):
            heading_text = line.replace('## ', '').strip()
            story.append(Paragraph(heading_text, section_heading))
        elif line.startswith('# '):
            heading_text = line.replace('# ', '').strip()
            story.append(Paragraph(heading_text, section_heading))
        elif line.startswith('- ') or line.startswith('* '):
            item_text = line[2:].strip()
            item_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', item_text)
            story.append(Paragraph(f'&bull; {item_text}', bullet_style))
        else:
            para_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            story.append(Paragraph(para_text, body_style))

    # Disclaimer
    story.append(HRFlowable(width='100%', thickness=0.8, color=colors.HexColor('#cccccc'), spaceBefore=12, spaceAfter=6))
    story.append(Paragraph('<b>Disclaimer & Data Sources:</b> Market data retrieved from Yahoo Finance (NSE/BSE). AI research memos are powered by NVIDIA NIM (Google Gemma model) and grounded strictly on verified financial metrics. This document is automatically generated for educational and informational research purposes only and does not constitute investment advice.', disclaimer_style))

    doc.build(story)
    return buffer.getvalue()

# ---------------------------------------------------------
# Section A — Application Header & Top-Right Stock Search
# ---------------------------------------------------------
current_ts_str = datetime.now().strftime("%d %b %Y • %H:%M IST")

PRESET_STOCKS = {
    "Reliance Industries (RELIANCE)": "RELIANCE.NS",
    "Tata Consultancy Services (TCS)": "TCS.NS",
    "HDFC Bank (HDFCBANK)": "HDFCBANK.NS",
    "Tata Motors (TMCV)": "TMCV.NS",
    "Infosys (INFY)": "INFY.NS",
    "ICICI Bank (ICICIBANK)": "ICICIBANK.NS",
    "State Bank of India (SBIN)": "SBIN.NS",
    "Bharti Airtel (BHARTIARTL)": "BHARTIARTL.NS",
    "ITC Limited (ITC)": "ITC.NS",
    "Larsen & Toubro (LT)": "LT.NS",
    "Hindustan Unilever (HINDUNILVR)": "HINDUNILVR.NS",
    "Bajaj Finance (BAJFINANCE)": "BAJFINANCE.NS",
    "Sun Pharma (SUNPHARMA)": "SUNPHARMA.NS",
    "Maruti Suzuki (MARUTI)": "MARUTI.NS",
    "Adani Enterprises (ADANIENT)": "ADANIENT.NS",
    "Kotak Mahindra Bank (KOTAKBANK)": "KOTAKBANK.NS",
    "Axis Bank (AXISBANK)": "AXISBANK.NS",
    "Wipro (WIPRO)": "WIPRO.NS",
    "HCL Technologies (HCLTECH)": "HCLTECH.NS",
    "NTPC Limited (NTPC)": "NTPC.NS",
    "🔍 Enter Custom Ticker...": "CUSTOM"
}

with st.container(border=True):
    col_brand, col_search = st.columns([5.8, 4.2], vertical_alignment="center")

    with col_brand:
        st.markdown(f"""
        <div class="masthead-left">
            <div class="masthead-logo">📈</div>
            <div>
                <div class="masthead-title">EquityLens AI</div>
                <div style="display: flex; align-items: center; gap: 8px; margin-top: 3px; flex-wrap: wrap;">
                    <span class="masthead-subtitle">Equity Research Workspace</span>
                    <span style="color: #334155;">&bull;</span>
                    <span class="status-pill">● NSE/BSE DELAYED (15m)</span>
                    <span style="color: #334155;">&bull;</span>
                    <span class="masthead-timestamp">{current_ts_str}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_search:
        selection = st.selectbox(
            "SEARCH LISTED EQUITY",
            options=list(PRESET_STOCKS.keys()),
            index=0,
            label_visibility="collapsed",
            help="Select a company from the preset list or choose 'Enter Custom Ticker...'"
        )

        if selection == "🔍 Enter Custom Ticker...":
            custom_input = st.text_input(
                "Enter Symbol",
                value="WIPRO.NS",
                placeholder="e.g. WIPRO.NS or 500325.BO",
                label_visibility="collapsed",
                help="Append .NS for NSE stocks or .BO for BSE listings."
            ).strip().upper()
            active_ticker = custom_input
        else:
            active_ticker = PRESET_STOCKS[selection]

# Clean up ticker if user entered ticker without exchange suffix
if not (active_ticker.endswith(".NS") or active_ticker.endswith(".BO")):
    active_ticker = f"{active_ticker}.NS"

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------
with st.spinner(f"Loading market data for {active_ticker}..."):
    company_info = get_company_data(active_ticker)

if not company_info:
    st.error(f"⚠️ Could not load data for symbol **{active_ticker}**.")
    st.info(
        "**Tips for Indian Listed Equities:**\n"
        "- Ensure the symbol ends with `.NS` for the National Stock Exchange (e.g. `INFY.NS`, `RELIANCE.NS`).\n"
        "- Alternatively, use `.BO` for Bombay Stock Exchange listings (e.g. `500325.BO` or `TCS.BO`)."
    )
else:
    # ---------------------------------------------------------
    # Section B — Company Identity and Current Price
    # ---------------------------------------------------------
    company_name = company_info.get("shortName") or company_info.get("longName") or active_ticker
    sector = company_info.get("sector", "N/A")
    industry = company_info.get("industry", "N/A")
    currency = company_info.get("currency", "INR")
    current_price = company_info.get("currentPrice") or company_info.get("regularMarketPrice")
    prev_close = company_info.get("previousClose") or company_info.get("regularMarketPreviousClose")

    price_change = None
    price_change_pct = None
    if current_price and prev_close:
        price_change = current_price - prev_close
        price_change_pct = (price_change / prev_close) * 100

    col_identity, col_price = st.columns([65, 35])

    with col_identity:
        st.markdown(f"""
        <div class="company-banner">
            <div class="eyebrow-label">COMPANY OVERVIEW</div>
            <h1 class="company-title">{company_name}</h1>
            <div style="margin-top: 8px;">
                <span class="tag-badge"><b>TICKER:</b> {active_ticker}</span>
                <span class="tag-badge"><b>EXCHANGE:</b> NSE / BSE</span>
                <span class="tag-badge"><b>SECTOR:</b> {sector}</span>
                <span class="tag-badge"><b>INDUSTRY:</b> {industry}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_price:
        if current_price:
            price_val_str = f"₹{current_price:,.2f}"
            if price_change is not None and price_change_pct is not None:
                if price_change >= 0:
                    delta_badge = f'<span class="price-delta-positive">▲ +₹{price_change:,.2f} (+{price_change_pct:+.2f}%)</span>'
                else:
                    delta_badge = f'<span class="price-delta-negative">▼ -₹{abs(price_change):,.2f} ({price_change_pct:+.2f}%)</span>'
            else:
                delta_badge = '<span class="price-delta-positive">—</span>'
            prev_str = f"Prev Close: ₹{prev_close:,.2f}" if prev_close else "Prev Close: N/A"
        else:
            price_val_str = "N/A"
            delta_badge = ""
            prev_str = ""

        st.markdown(f"""
        <div class="company-banner">
            <div class="eyebrow-label">CURRENT PRICE</div>
            <div class="price-value">{price_val_str}</div>
            <div>{delta_badge}</div>
            <div class="price-meta">{prev_str} &bull; Real-time quote (NSE/BSE)</div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Section C — Fundamental Snapshot
    # ---------------------------------------------------------
    st.markdown('<div class="section-header">📊 Fundamental Snapshot</div>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    # 1. Market Capitalisation
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div>
                <div class="metric-label">Market Capitalisation</div>
                <div class="metric-value">{format_inr(company_info.get("marketCap"))}</div>
            </div>
            <div class="metric-sub">Total Valuation</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. P/E Ratio
    with col2:
        pe_val = format_ratio(company_info.get("trailingPE"))
        fwd_pe = format_ratio(company_info.get("forwardPE"))
        st.markdown(f"""
        <div class="metric-card">
            <div>
                <div class="metric-label">P/E Ratio</div>
                <div class="metric-value">{pe_val}</div>
            </div>
            <div class="metric-sub">Forward P/E: {fwd_pe}</div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Return on Equity
    with col3:
        roe_val = format_percent(company_info.get("returnOnEquity"))
        st.markdown(f"""
        <div class="metric-card">
            <div>
                <div class="metric-label">Return on Equity</div>
                <div class="metric-value">{roe_val}</div>
            </div>
            <div class="metric-sub">Profitability Efficiency</div>
        </div>
        """, unsafe_allow_html=True)

    # 4. Earnings Per Share
    with col4:
        eps_val = format_inr(company_info.get("trailingEps"))
        st.markdown(f"""
        <div class="metric-card">
            <div>
                <div class="metric-label">Earnings Per Share</div>
                <div class="metric-value">{eps_val}</div>
            </div>
            <div class="metric-sub">Trailing 12 Months</div>
        </div>
        """, unsafe_allow_html=True)

    # 5. Net Profit Margin
    with col5:
        margin_val = format_percent(company_info.get("profitMargins"))
        st.markdown(f"""
        <div class="metric-card">
            <div>
                <div class="metric-label">Net Profit Margin</div>
                <div class="metric-value">{margin_val}</div>
            </div>
            <div class="metric-sub">Operating Efficiency</div>
        </div>
        """, unsafe_allow_html=True)

    # 6. 52-Week Range
    with col6:
        high_52 = company_info.get("fiftyTwoWeekHigh")
        low_52 = company_info.get("fiftyTwoWeekLow")
        range_52 = f"₹{low_52:,.0f} - ₹{high_52:,.0f}" if (high_52 and low_52) else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div>
                <div class="metric-label">52-Week Range</div>
                <div class="metric-value" style="font-size: 1.05rem;">{range_52}</div>
            </div>
            <div class="metric-sub">52W Low / High</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Section D — Historical Price Action
    # ---------------------------------------------------------
    st.markdown('<div class="section-header">📈 Historical Price Action</div>', unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns([1, 4])
    with chart_col1:
        st.markdown('<div class="chart-controls-panel">', unsafe_allow_html=True)
        time_period = st.radio(
            "TIMEFRAME",
            options=["1mo", "6mo", "1y", "5y"],
            format_func=lambda x: {"1mo": "1 Month", "6mo": "6 Months", "1y": "1 Year", "5y": "5 Years"}[x],
            index=2
        )
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        chart_style = st.selectbox("CHART TYPE", ["Candlestick", "Line Chart"], index=0)
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        show_volume = st.checkbox("Show Volume", value=True)
        st.markdown('</div>', unsafe_allow_html=True)

    df_hist = get_historical_prices(active_ticker, time_period)

    with chart_col2:
        if df_hist is not None and not df_hist.empty:
            if show_volume:
                fig = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.06,
                    row_heights=[0.75, 0.25]
                )
            else:
                fig = make_subplots(rows=1, cols=1)

            if chart_style == "Candlestick":
                fig.add_trace(
                    go.Candlestick(
                        x=df_hist.index,
                        open=df_hist['Open'],
                        high=df_hist['High'],
                        low=df_hist['Low'],
                        close=df_hist['Close'],
                        name="Price (₹)",
                        increasing_line_color="#10b981",
                        increasing_fillcolor="#10b981",
                        decreasing_line_color="#f43f5e",
                        decreasing_fillcolor="#f43f5e"
                    ),
                    row=1, col=1
                )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=df_hist.index,
                        y=df_hist['Close'],
                        mode='lines',
                        name='Closing Price (₹)',
                        line=dict(color='#38bdf8', width=2)
                    ),
                    row=1, col=1
                )

            # Volume Bar Chart
            if show_volume:
                volume_colors = ['#10b981' if c >= o else '#f43f5e' for c, o in zip(df_hist['Close'], df_hist['Open'])]
                fig.add_trace(
                    go.Bar(
                        x=df_hist.index,
                        y=df_hist['Volume'],
                        name="Volume",
                        marker_color=volume_colors,
                        opacity=0.5
                    ),
                    row=2, col=1
                )

            fig.update_layout(
                paper_bgcolor="#121620",
                plot_bgcolor="#121620",
                font=dict(family="Inter, -apple-system, sans-serif", color="#94a3b8", size=11),
                xaxis_rangeslider_visible=False,
                height=460,
                margin=dict(l=20, r=40, t=10, b=10),
                hovermode="x unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(color="#cbd5e1")
                )
            )
            fig.update_xaxes(
                showgrid=True,
                gridcolor="#1e2433",
                linecolor="#1e2433",
                tickfont=dict(color="#94a3b8")
            )
            fig.update_yaxes(
                showgrid=True,
                gridcolor="#1e2433",
                linecolor="#1e2433",
                tickfont=dict(color="#94a3b8"),
                side="right"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No historical price data available for the chosen timeframe.")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Section E — Company Profile & Operations
    # ---------------------------------------------------------
    summary_text = company_info.get("longBusinessSummary")
    city = company_info.get("city", "N/A")
    country = company_info.get("country", "India")
    website = company_info.get("website", "")
    employees = company_info.get("fullTimeEmployees")
    emp_str = f"{employees:,}" if employees else "N/A"

    with st.expander("🏢 Company Profile & Corporate Overview", expanded=False):
        st.markdown(f"""
        <div class="profile-card">
            <div class="profile-meta-grid">
                <div class="profile-meta-item">
                    HEADQUARTERS
                    <div class="profile-meta-val">{city}, {country}</div>
                </div>
                <div class="profile-meta-item">
                    FULL-TIME EMPLOYEES
                    <div class="profile-meta-val">{emp_str}</div>
                </div>
                <div class="profile-meta-item">
                    SECTOR & INDUSTRY
                    <div class="profile-meta-val">{sector} &bull; {industry}</div>
                </div>
                <div class="profile-meta-item">
                    OFFICIAL WEBSITE
                    <div class="profile-meta-val">{'<a href="' + website + '" target="_blank" style="color: #38bdf8; text-decoration: none;">' + website + '</a>' if website else 'N/A'}</div>
                </div>
            </div>
            <div class="profile-text">
                {summary_text if summary_text else 'Corporate business description not available for this listing.'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Section F — AI Equity Research Memo
    # ---------------------------------------------------------
    st.markdown('<div class="section-header">🧠 AI Equity Research Memo</div>', unsafe_allow_html=True)

    memo_key = f"ai_memo_{active_ticker}"
    if memo_key not in st.session_state:
        st.session_state[memo_key] = None

    nvidia_key = get_nvidia_api_key()

    if not nvidia_key:
        st.info("🔒 **Backend Notice:** The AI research analyst is powered by NVIDIA Gemma. To enable it, please add your `NVIDIA_API_KEY` to your `.env` file or cloud deployment Secrets.")
    else:
        btn_col, _ = st.columns([1, 3])
        with btn_col:
            generate_clicked = st.button("⚡ Generate AI Research Memo", type="primary", use_container_width=True)

        if generate_clicked:
            with st.spinner(f"Analyzing {company_name}..."):
                # Fetch 1-year history specifically for AI analysis context
                df_for_ai = get_historical_prices(active_ticker, "1y")
                memo_text, error_msg = generate_ai_research_memo(
                    company_name, active_ticker, company_info, df_for_ai
                )
                if error_msg:
                    st.error(f"AI Generation Error: {error_msg}")
                else:
                    st.session_state[memo_key] = {
                        "text": memo_text,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

        # Render Memo if available in state
        if st.session_state[memo_key]:
            memo_data = st.session_state[memo_key]
            st.markdown(f"""
            <div class="ai-card">
                <div class="ai-header-bar">
                    <div>
                        <div class="ai-title">Institutional Analyst Note — {company_name} ({active_ticker})</div>
                        <div style="font-size: 0.75rem; color: #64748b; margin-top: 2px;">
                            Generated at {memo_data['timestamp']} &bull; Sourced from verified market fundamentals
                        </div>
                    </div>
                    <span class="ai-model-badge">NVIDIA NIM &bull; Google Gemma 4 (31B IT)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(memo_data["text"])

            # ---------------------------------------------------------
            # Downloadable Institutional PDF Research Report
            # ---------------------------------------------------------
            pdf_bytes = generate_pdf_report(
                company_name=company_name,
                symbol=active_ticker,
                sector=sector,
                industry=industry,
                price_str=f"Rs. {current_price:,.2f}" if current_price else "N/A",
                metrics_dict={
                    "Market Cap": format_inr(company_info.get("marketCap")),
                    "Trailing P/E": format_ratio(company_info.get("trailingPE")),
                    "Forward P/E": format_ratio(company_info.get("forwardPE")),
                    "ROE": format_percent(company_info.get("returnOnEquity")),
                    "Trailing EPS": format_inr(company_info.get("trailingEps")),
                    "Net Margin": format_percent(company_info.get("profitMargins")),
                    "52-Week Range": range_52
                },
                memo_text=memo_data["text"],
                timestamp=memo_data["timestamp"]
            )

            st.download_button(
                label="📥 Download Equity Research Report (.pdf)",
                data=pdf_bytes,
                file_name=f"EquityLens_Report_{active_ticker.replace('.', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=False
            )
