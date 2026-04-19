import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import os

st.set_page_config(
    page_title="InsightFlow AI Dashboard",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0f1117; color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #161b27; border-right: 1px solid rgba(255,255,255,0.07); }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    div[data-testid="stMetric"] { background-color: #161b27 !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 10px !important; padding: 16px !important; }
    div[data-testid="stMetricValue"] > div { color: #e2e8f0 !important; }
    div[data-testid="stMetricLabel"] > div { color: rgba(255,255,255,0.4) !important; }
    h1 { color: #a89ef8 !important; }
    h2, h3 { color: #e2e8f0 !important; }
    [data-testid="stFileUploader"] { background-color: #161b27; border: 2px dashed rgba(124,110,247,0.3); border-radius: 12px; padding: 10px; }
    .stButton button { background: linear-gradient(135deg, #1e5799, #38bdf8) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 500 !important; }
    [data-testid="stDataFrame"] { background-color: #161b27; border-radius: 10px; }
    .insight-box { background: rgba(30,87,153,0.1); border: 1px solid rgba(56,189,248,0.25); border-radius: 10px; padding: 16px 18px; margin: 10px 0; }
    .insight-label { font-size: 11px; color: #38bdf8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px; }
    .insight-text { font-size: 13px; color: rgba(255,255,255,0.65); line-height: 1.7; white-space: pre-line; }
    .section-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.2); margin-bottom: 8px; margin-top: 16px; }
    .success-box { background: rgba(56,189,248,0.08); border: 1px solid rgba(56,189,248,0.25); border-radius: 8px; padding: 10px 14px; color: #38bdf8; font-size: 13px; margin-bottom: 16px; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Gemini Setup ─────────────────────────────────────────────────────────────
GEMINI_API_KEY = ""
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ─── Chart Colors ─────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#161b27",
    plot_bgcolor="#161b27",
    font=dict(color="rgba(255,255,255,0.5)", size=11),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", color="rgba(255,255,255,0.3)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", color="rgba(255,255,255,0.3)"),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(font=dict(color="rgba(255,255,255,0.5)"), bgcolor="rgba(0,0,0,0)")
)
BLUE_SCALE    = ["#1a3a6b", "#1e5799", "#2196c4", "#38bdf8", "#7dd3fc"]
VIOLET_SCALE  = ["#2e1065", "#4c1d95", "#6d28d9", "#7c3aed", "#8b5cf6", "#a78bfa", "#c4b5fd", "#ddd6fe"]
REGION_COLORS = ["#1e5799", "#38bdf8", "#2196c4", "#7dd3fc"]
LINE_COLOR    = "#38bdf8"

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 InsightFlow")
    st.markdown("---")
    st.markdown("**Workspace**")
    st.markdown("🔵 Overview")
    st.markdown("🤖 AI Analysis")
    st.markdown("📈 Charts")
    st.markdown("📋 Reports")
    st.markdown("---")
    st.markdown("**Data**")
    st.markdown("📁 Datasets")
    st.markdown("🕓 History")
    st.markdown("---")
    st.markdown("<div style='color:rgba(255,255,255,0.2);font-size:11px;'>© 2026 InsightFlow v2.0</div>", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 📊 InsightFlow AI Dashboard")
st.markdown("<div style='color:rgba(255,255,255,0.3);font-size:13px;margin-top:-10px;margin-bottom:20px;'>AI-powered data analytics — upload any CSV to get started</div>", unsafe_allow_html=True)

# ─── Upload ───────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("", type=["csv"], label_visibility="collapsed")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    if "profit" not in df.columns and "sales" in df.columns:
        df["profit"] = (df["sales"] * 0.2).round(2)

    st.markdown(f"<div class='success-box'>✅ <b>{uploaded_file.name}</b> — {len(df)} rows · {len(df.columns)} columns</div>", unsafe_allow_html=True)

    # ── Detect columns ──
    sales_col   = next((c for c in ["sales","revenue","amount","total"] if c in df.columns), None)
    product_col = next((c for c in ["product_name","product","item","name"] if c in df.columns), None)

    # ── Filters ──
    fc1, fc2, fc3, fc4 = st.columns([2, 2, 1.5, 1.5])
    with fc1:
        if "region" in df.columns:
            regions = ["All"] + sorted(df["region"].dropna().unique().tolist())
            region = st.selectbox("Region", regions)
            if region != "All":
                df = df[df["region"] == region]
    with fc2:
        if "category" in df.columns:
            cats = ["All"] + sorted(df["category"].dropna().unique().tolist())
            category = st.selectbox("Category", cats)
            if category != "All":
                df = df[df["category"] == category]
    with fc3:
        start_date = st.date_input("From", value=None)
    with fc4:
        end_date = st.date_input("To", value=None)

    if start_date and "order_date" in df.columns:
        df = df[df["order_date"] >= pd.to_datetime(start_date)]
    if end_date and "order_date" in df.columns:
        df = df[df["order_date"] <= pd.to_datetime(end_date)]

    # ── Metrics ──
    st.markdown("<div class='section-label'>Summary</div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Records",  f"{len(df):,}")
    m2.metric("Total Revenue",  f"${df[sales_col].sum():,.2f}"  if sales_col else "N/A")
    m3.metric("Avg Sale Value", f"${df[sales_col].mean():,.2f}" if sales_col else "N/A")
    m4.metric("Categories",     df["category"].nunique() if "category" in df.columns else len(df.columns))

    # ── AI Insight ──
    st.markdown("<div class='section-label'>AI Insight</div>", unsafe_allow_html=True)
    ai_placeholder = st.empty()

    if "ai_summary" not in st.session_state:
        st.session_state.ai_summary = "Click 'Generate' to analyze your data with Gemini AI."

    _, btn_col = st.columns([5, 1])
    with btn_col:
        generate = st.button("✦ Generate")

    if generate:
        if not GEMINI_API_KEY:
            st.session_state.ai_summary = "❌ Gemini API key not found. Add GEMINI_API_KEY in Streamlit secrets."
        else:
            with st.spinner("Analyzing your data..."):
                try:
                    genai.configure(api_key=GEMINI_API_KEY)
                    sample = df.head(10).fillna("N/A").to_string(index=False)
                    prompt = f"""You are a data analyst. Analyze this dataset and provide 4 key insights in bullet points.
Focus on trends, top performers, and actionable recommendations.

Dataset sample:
{sample}

Total rows: {len(df)}
Keep insights short and actionable."""
                    model = genai.GenerativeModel("gemini-2.0-flash")
                    response = model.generate_content(prompt)
                    st.session_state.ai_summary = response.text
                except Exception as e:
                    st.session_state.ai_summary = f"❌ AI Error: {str(e)}"

    ai_placeholder.markdown(f"""
    <div class='insight-box'>
        <div class='insight-label'>✦ AI Insight — Gemini 2.0 Flash</div>
        <div class='insight-text'>{st.session_state.ai_summary}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Charts Row 1 ──
    st.markdown("<div class='section-label'>Charts</div>", unsafe_allow_html=True)
    ch1, ch2 = st.columns(2)

    with ch1:
        if product_col and sales_col:
            # Show ALL products sorted by sales
            all_products = (
                df.groupby(product_col)[sales_col]
                .sum()
                .reset_index()
                .sort_values(sales_col, ascending=True)
            )
            fig = px.bar(
                all_products,
                x=sales_col,
                y=product_col,
                orientation="h",
                title=f"🧊 All Products by Revenue ({len(all_products)} products)",
                color=sales_col,
                color_continuous_scale=BLUE_SCALE
            )
            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_layout(
                height=max(400, len(all_products) * 25),
                coloraxis_colorbar=dict(
                    tickfont=dict(color="rgba(255,255,255,0.4)"),
                    title=dict(font=dict(color="rgba(255,255,255,0.4)"), text="Sales")
                )
            )
            st.plotly_chart(fig, use_container_width=True)

    with ch2:
        if "category" in df.columns and sales_col:
            pbc = df.groupby("category")[sales_col].sum().reset_index()
            n = len(pbc)
            violet_colors = (VIOLET_SCALE * ((n // len(VIOLET_SCALE)) + 1))[:n]
            fig = px.pie(
                pbc,
                names="category",
                values=sales_col,
                title="🟣 Revenue by Category",
                color_discrete_sequence=violet_colors,
                hole=0.4
            )
            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_traces(
                textfont_color="white",
                textfont_size=12,
                marker=dict(line=dict(color="#0f1117", width=2))
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Charts Row 2 ──
    ch3, ch4 = st.columns(2)

    with ch3:
        if "region" in df.columns and sales_col:
            sbr = df.groupby("region")[sales_col].sum().reset_index()
            fig = px.bar(
                sbr, x="region", y=sales_col,
                title="📊 Sales by Region",
                color="region",
                color_discrete_sequence=REGION_COLORS
            )
            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

    with ch4:
        if "order_date" in df.columns and sales_col:
            trend = df.groupby(df["order_date"].dt.date)[sales_col].sum().reset_index()
            fig = px.line(
                trend, x="order_date", y=sales_col,
                title="📈 Sales Trend Over Time",
                color_discrete_sequence=[LINE_COLOR]
            )
            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_traces(line_width=2)
            st.plotly_chart(fig, use_container_width=True)

    # ── Data Table ──
    st.markdown("<div class='section-label'>Data Preview</div>", unsafe_allow_html=True)
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)

else:
    st.markdown("""
    <div style='text-align:center;padding:80px 20px;'>
        <div style='font-size:48px;margin-bottom:16px;'>📂</div>
        <div style='font-size:16px;color:rgba(255,255,255,0.4);margin-bottom:8px;'>Upload a CSV file to get started</div>
        <div style='font-size:13px;color:rgba(255,255,255,0.2);'>Any CSV dataset works — sales, finance, marketing, HR and more</div>
    </div>
    """, unsafe_allow_html=True)
