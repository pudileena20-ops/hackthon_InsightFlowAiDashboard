import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import os

st.set_page_config(
    page_title="InsightFlow AI Dashboard",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# ─── Dark Theme CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; color: #e2e8f0; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b27;
        border-right: 1px solid rgba(255,255,255,0.07);
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: #161b27;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px;
        padding: 16px;
    }
    [data-testid="metric-container"] label {
        color: rgba(255,255,255,0.4) !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #e2e8f0 !important;
        font-size: 24px !important;
        font-weight: 500 !important;
    }

    /* Headers */
    h1 { color: #a89ef8 !important; font-size: 22px !important; }
    h2 { color: #e2e8f0 !important; font-size: 18px !important; }
    h3 { color: #e2e8f0 !important; font-size: 16px !important; }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #161b27;
        border: 2px dashed rgba(124,110,247,0.3);
        border-radius: 12px;
        padding: 10px;
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #7c6ef7, #f97316);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        width: 100%;
    }
    .stButton button:hover { opacity: 0.9; }

    /* Selectbox */
    [data-testid="stSelectbox"] select,
    .stSelectbox > div > div {
        background-color: #161b27 !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        background-color: #161b27;
        border-radius: 10px;
    }

    /* Cards */
    .insight-box {
        background: rgba(124,110,247,0.07);
        border: 1px solid rgba(124,110,247,0.25);
        border-radius: 10px;
        padding: 16px 18px;
        margin: 10px 0;
    }
    .insight-label {
        font-size: 11px;
        color: #a89ef8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 8px;
    }
    .insight-text {
        font-size: 13px;
        color: rgba(255,255,255,0.65);
        line-height: 1.7;
    }
    .section-label {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: rgba(255,255,255,0.2);
        margin-bottom: 8px;
        margin-top: 16px;
    }
    .success-box {
        background: rgba(74,222,128,0.08);
        border: 1px solid rgba(74,222,128,0.25);
        border-radius: 8px;
        padding: 10px 14px;
        color: #4ade80;
        font-size: 13px;
        margin-bottom: 16px;
    }
    /* Hide default streamlit elements */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Gemini Setup ─────────────────────────────────────────────────────────────
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = os.environ.get("GEMINI_API_KEY", "")

if api_key:
    genai.configure(api_key=api_key)

# ─── Plotly dark theme ────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#161b27",
    plot_bgcolor="#161b27",
    font=dict(color="rgba(255,255,255,0.5)", size=11),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", color="rgba(255,255,255,0.3)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", color="rgba(255,255,255,0.3)"),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(font=dict(color="rgba(255,255,255,0.4)"))
)
BAR_COLORS  = ["#7c6ef7","#f97316","#a855f7","#fb923c","#9333ea","#fdba74"]
PIE_COLORS  = ["#7c6ef7","#f97316","#a855f7","#fb923c","#9333ea","#fdba74"]
LINE_COLOR  = "#f97316"

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
    st.markdown(
        "<div style='color:rgba(255,255,255,0.2);font-size:11px;'>© 2026 InsightFlow v2.0</div>",
        unsafe_allow_html=True
    )

# ─── Main Content ─────────────────────────────────────────────────────────────
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

    st.markdown(f"<div class='success-box'>✅ <b>{uploaded_file.name}</b> loaded — {len(df)} rows · {len(df.columns)} columns</div>", unsafe_allow_html=True)

    # ── Filters ──
    with st.container():
        fc1, fc2, fc3, fc4 = st.columns([2, 2, 1.5, 1.5])
        with fc1:
            if "region" in df.columns:
                regions = ["All Regions"] + sorted(df["region"].dropna().unique().tolist())
                region = st.selectbox("Region", regions)
                if region != "All Regions":
                    df = df[df["region"] == region]
        with fc2:
            if "category" in df.columns:
                cats = ["All Categories"] + sorted(df["category"].dropna().unique().tolist())
                category = st.selectbox("Category", cats)
                if category != "All Categories":
                    df = df[df["category"] == category]
        with fc3:
            start_date = st.date_input("From", value=None, label_visibility="visible")
        with fc4:
            end_date = st.date_input("To", value=None, label_visibility="visible")

        if start_date and "order_date" in df.columns:
            df = df[df["order_date"] >= pd.to_datetime(start_date)]
        if end_date and "order_date" in df.columns:
            df = df[df["order_date"] <= pd.to_datetime(end_date)]

    # ── Metrics ──
    st.markdown("<div class='section-label'>Summary</div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Rows",    f"{len(df):,}")
    m2.metric("Total Sales",   f"{df['sales'].sum():,.0f}"  if "sales"  in df.columns else "N/A")
    m3.metric("Total Profit",  f"{df['profit'].sum():,.0f}" if "profit" in df.columns else "N/A")
    m4.metric("Total Columns", len(df.columns))

    # ── AI Insight ──
    st.markdown("<div class='section-label'>AI Insight</div>", unsafe_allow_html=True)
    ai_placeholder = st.empty()

    if "ai_summary" not in st.session_state:
        st.session_state.ai_summary = "Click 'Generate Insights' to analyze your data."

    col_ai1, col_ai2 = st.columns([5, 1])
    with col_ai2:
        if st.button("Generate Insights"):
            with st.spinner("Analyzing..."):
                try:
                    sample = df.head(10).fillna("N/A").to_string(index=False)
                    prompt = f"""You are a data analyst. Analyze this sales dataset and provide 4 key insights in bullet points.
Focus on trends, top performers, and recommendations.
Dataset sample:
{sample}
Total rows: {len(df)}
Keep insights short and actionable."""
                    model = genai.GenerativeModel("gemini-2.0-flash")
                    response = model.generate_content(prompt)
                    st.session_state.ai_summary = response.text
                except Exception as e:
                    st.session_state.ai_summary = f"Error: {e}"

    ai_placeholder.markdown(f"""
    <div class='insight-box'>
        <div class='insight-label'>✦ AI Insight — Gemini 2.0</div>
        <div class='insight-text'>{st.session_state.ai_summary}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Charts Row 1 ──
    st.markdown("<div class='section-label'>Charts</div>", unsafe_allow_html=True)
    ch1, ch2 = st.columns([2, 1])
    with ch1:
        if "region" in df.columns and "sales" in df.columns:
            sbr = df.groupby("region")["sales"].sum().reset_index()
            fig = px.bar(sbr, x="region", y="sales", title="Sales by Region",
                        color="region", color_discrete_sequence=BAR_COLORS)
            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_traces(marker_line_width=0, width=0.5)
            st.plotly_chart(fig, use_container_width=True)
    with ch2:
        if "category" in df.columns and "profit" in df.columns:
            pbc = df.groupby("category")["profit"].sum().reset_index()
            fig = px.pie(pbc, names="category", values="profit",
                        title="Profit by Category",
                        color_discrete_sequence=PIE_COLORS,
                        hole=0.4)
            fig.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

    # ── Charts Row 2 ──
    ch3, ch4 = st.columns(2)
    with ch3:
        if "order_date" in df.columns and "sales" in df.columns:
            trend = df.groupby(df["order_date"].dt.date)["sales"].sum().reset_index()
            fig = px.line(trend, x="order_date", y="sales",
                         title="Sales Trend Over Time",
                         color_discrete_sequence=[LINE_COLOR])
            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_traces(line_width=2)
            st.plotly_chart(fig, use_container_width=True)
    with ch4:
        product_col = next((c for c in ["product_name","product","item","name"] if c in df.columns), None)
        if product_col and "sales" in df.columns:
            top5 = df.groupby(product_col)["sales"].sum().nlargest(5).reset_index()
            fig = px.bar(top5, x="sales", y=product_col,
                        orientation="h", title="Top 5 Products",
                        color_discrete_sequence=["#7c6ef7"])
            fig.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

    # ── Data Table ──
    st.markdown("<div class='section-label'>Data Preview</div>", unsafe_allow_html=True)
    st.dataframe(
        df.head(10),
        use_container_width=True,
        hide_index=True
    )

else:
    # No file uploaded state
    st.markdown("""
    <div style='text-align:center;padding:80px 20px;'>
        <div style='font-size:48px;margin-bottom:16px;'>📂</div>
        <div style='font-size:16px;color:rgba(255,255,255,0.4);margin-bottom:8px;'>Upload a CSV file to get started</div>
        <div style='font-size:13px;color:rgba(255,255,255,0.2);'>Any CSV dataset works — sales, finance, marketing, HR and more</div>
    </div>
    """, unsafe_allow_html=True)
