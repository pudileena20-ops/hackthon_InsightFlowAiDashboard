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
    .stButton button:hover { opacity: 0.9 !important; }
    [data-testid="stDataFrame"] { background-color: #161b27 !important; border-radius: 10px; }
    .insight-box { background: rgba(30,87,153,0.1); border: 1px solid rgba(56,189,248,0.25); border-radius: 10px; padding: 16px 18px; margin: 10px 0; }
    .insight-label { font-size: 11px; color: #38bdf8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px; }
    .insight-text { font-size: 13px; color: rgba(255,255,255,0.65); line-height: 1.7; white-space: pre-line; }
    .section-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.2); margin-bottom: 8px; margin-top: 16px; }
    .success-box { background: rgba(56,189,248,0.08); border: 1px solid rgba(56,189,248,0.25); border-radius: 8px; padding: 10px 14px; color: #38bdf8; font-size: 13px; margin-bottom: 16px; }
    .filter-box { background: #161b27; border: 1px solid rgba(255,255,255,0.07); border-radius: 10px; padding: 16px 18px; margin-bottom: 20px; }
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
BLUE_SCALE    = ["#1a3a6b","#1e5799","#2196c4","#38bdf8","#7dd3fc"]
VIOLET_SCALE  = ["#2e1065","#4c1d95","#6d28d9","#7c3aed","#8b5cf6","#a78bfa","#c4b5fd","#ddd6fe"]
REGION_COLORS = ["#1e5799","#38bdf8","#2196c4","#7dd3fc"]
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
    df_original = pd.read_csv(uploaded_file)
    df_original.columns = df_original.columns.str.strip().str.lower().str.replace(" ", "_")
    if "order_date" in df_original.columns:
        df_original["order_date"] = pd.to_datetime(df_original["order_date"], errors="coerce")
    if "profit" not in df_original.columns and "sales" in df_original.columns:
        df_original["profit"] = (df_original["sales"] * 0.2).round(2)

    st.markdown(f"<div class='success-box'>✅ <b>{uploaded_file.name}</b> — {len(df_original)} rows · {len(df_original.columns)} columns</div>", unsafe_allow_html=True)

    # ── Detect columns ──
    sales_col   = next((c for c in ["sales","revenue","amount","total"] if c in df_original.columns), None)
    product_col = next((c for c in ["product_name","product","item","name"] if c in df_original.columns), None)

    # ─── Filters ──────────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Filters</div>", unsafe_allow_html=True)

    with st.container():
        f1, f2, f3, f4, f5 = st.columns([2, 2, 2, 2, 1])

        with f1:
            region_options = ["All Regions"]
            if "region" in df_original.columns:
                region_options += sorted(df_original["region"].dropna().unique().tolist())
            selected_region = st.selectbox("🌍 Region", region_options)

        with f2:
            category_options = ["All Categories"]
            if "category" in df_original.columns:
                category_options += sorted(df_original["category"].dropna().unique().tolist())
            selected_category = st.selectbox("📦 Category", category_options)

        with f3:
            start_date = st.date_input("📅 From Date", value=None)

        with f4:
            end_date = st.date_input("📅 To Date", value=None)

        with f5:
            st.markdown("<br>", unsafe_allow_html=True)
            apply = st.button("✅ Apply")
            reset = st.button("🔄 Reset")

    # ── Apply Filters ──
    if reset:
        selected_region   = "All Regions"
        selected_category = "All Categories"
        start_date        = None
        end_date          = None

    df = df_original.copy()

    if selected_region != "All Regions" and "region" in df.columns:
        df = df[df["region"] == selected_region]

    if selected_category != "All Categories" and "category" in df.columns:
        df = df[df["category"] == selected_category]

    if start_date and "order_date" in df.columns:
        df = df[df["order_date"] >= pd.to_datetime(start_date)]

    if end_date and "order_date" in df.columns:
        df = df[df["order_date"] <= pd.to_datetime(end_date)]

    # Show active filters
    active = []
    if selected_region   != "All Regions":   active.append(f"Region: {selected_region}")
    if selected_category != "All Categories": active.append(f"Category: {selected_category}")
    if start_date: active.append(f"From: {start_date}")
    if end_date:   active.append(f"To: {end_date}")
    if active:
        st.info(f"🔍 Active filters: {' | '.join(active)} — {len(df)} rows")

    # ── Metrics ──
    st.markdown("<div class='section-label'>Summary</div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Records",  f"{len(df):,}")
    m2.metric("Total Sales",    f"${df[sales_col].sum():,.2f}"  if sales_col else "N/A")
    m3.metric("Avg Sale Value", f"${df[sales_col].mean():,.2f}" if sales_col else "N/A")
    m4.metric("Categories",     df["category"].nunique() if "category" in df.columns else "N/A")

    # ── AI Insight ──
    st.markdown("<div class='section-label'>AI Insight</div>", unsafe_allow_html=True)
    ai_placeholder = st.empty()

    if "ai_summary" not in st.session_state:
        st.session_state.ai_summary = "Click 'Generate Insights' to analyze your data with Gemini AI."

    if st.button("🤖 Generate AI Insights"):
        if not GEMINI_API_KEY:
            st.session_state.ai_summary = "❌ Gemini API key not found. Please add GEMINI_API_KEY in Streamlit secrets settings."
        else:
            with st.spinner("🔍 Analyzing your data with Gemini AI..."):
                try:
                    genai.configure(api_key=GEMINI_API_KEY)
                    sample = df.head(15).fillna("N/A").to_string(index=False)
                    prompt = f"""You are a senior data analyst. Analyze this sales dataset and provide exactly 4 key insights as bullet points.
Focus on: top products, regional performance, trends, and recommendations.

Dataset sample:
{sample}

Total rows: {len(df)}
Total sales: {df[sales_col].sum() if sales_col else 'N/A'}

Provide 4 bullet points. Keep each insight short and actionable."""
                    genai.configure(api_key=GEMINI_API_KEY)
                    model = genai.GenerativeModel("gemini-2.0-flash")
                    response = model.generate_content(prompt)
                    st.session_state.ai_summary = response.text
                except Exception as e:
                    st.session_state.ai_summary = f"❌ Error: {str(e)}"

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
            all_products = (
                df.groupby(product_col)[sales_col]
                .sum()
                .reset_index()
                .sort_values(sales_col, ascending=True)
            )
            fig = px.bar(
                all_products, x=sales_col, y=product_col,
                orientation="h",
                title=f"🧊 Products by Sales ({len(all_products)} total)",
                color=sales_col,
                color_continuous_scale=BLUE_SCALE
            )
            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_layout(height=max(400, len(all_products) * 28))
            st.plotly_chart(fig, use_container_width=True)

    with ch2:
        if "category" in df.columns and sales_col:
            pbc = df.groupby("category")[sales_col].sum().reset_index()
            n = len(pbc)
            violet_colors = (VIOLET_SCALE * ((n // len(VIOLET_SCALE)) + 1))[:n]
            fig = px.pie(
                pbc, names="category", values=sales_col,
                title="🟣 Sales by Category",
                color_discrete_sequence=violet_colors,
                hole=0.4
            )
            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_traces(textfont_color="white", textfont_size=12,
                            marker=dict(line=dict(color="#0f1117", width=2)))
            st.plotly_chart(fig, use_container_width=True)

    # ── Charts Row 2 ──
    ch3, ch4 = st.columns(2)

    with ch3:
        if "region" in df.columns and sales_col:
            sbr = df.groupby("region")[sales_col].sum().reset_index()
            fig = px.bar(sbr, x="region", y=sales_col,
                        title="📊 Sales by Region",
                        color="region",
                        color_discrete_sequence=REGION_COLORS)
            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

    with ch4:
        if "order_date" in df.columns and sales_col:
            trend = df.groupby(df["order_date"].dt.date)[sales_col].sum().reset_index()
            fig = px.line(trend, x="order_date", y=sales_col,
                         title="📈 Sales Trend Over Time",
                         color_discrete_sequence=[LINE_COLOR])
            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_traces(line_width=2)
            st.plotly_chart(fig, use_container_width=True)

    # ── Full Data Table ────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Full Data Table</div>", unsafe_allow_html=True)

    # Table search
    search = st.text_input("🔍 Search in table", placeholder="Type to search any value...")
    if search:
        mask = df.astype(str).apply(lambda col: col.str.contains(search, case=False)).any(axis=1)
        table_df = df[mask]
    else:
        table_df = df

    st.markdown(f"<div style='font-size:12px;color:rgba(255,255,255,0.3);margin-bottom:8px;'>Showing {len(table_df)} of {len(df)} rows</div>", unsafe_allow_html=True)

    st.dataframe(
        table_df.reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
        height=500
    )

    # ── Download Button ──
    csv = table_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv,
        file_name="insightflow_filtered_data.csv",
        mime="text/csv"
    )

else:
    st.markdown("""
    <div style='text-align:center;padding:80px 20px;'>
        <div style='font-size:48px;margin-bottom:16px;'>📂</div>
        <div style='font-size:16px;color:rgba(255,255,255,0.4);margin-bottom:8px;'>Upload a CSV file to get started</div>
        <div style='font-size:13px;color:rgba(255,255,255,0.2);'>Any CSV dataset works — sales, finance, marketing, HR and more</div>
    </div>
    """, unsafe_allow_html=True)
