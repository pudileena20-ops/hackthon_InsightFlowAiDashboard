import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import os

st.set_page_config(page_title="InsightFlow AI", layout="wide", page_icon="📊")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = os.environ.get("GEMINI_API_KEY", "")

genai.configure(api_key=api_key)

st.title("📊 InsightFlow AI Dashboard")
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    if "profit" not in df.columns and "sales" in df.columns:
        df["profit"] = (df["sales"] * 0.2).round(2)

    st.success(f"✅ {len(df)} rows loaded!")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Rows", len(df))
    m2.metric("Total Sales", f"{df['sales'].sum():,.0f}" if "sales" in df.columns else "N/A")
    m3.metric("Total Profit", f"{df['profit'].sum():,.0f}" if "profit" in df.columns else "N/A")
    m4.metric("Total Columns", len(df.columns))

    col1, col2 = st.columns(2)
    with col1:
        if "region" in df.columns and "sales" in df.columns:
            fig = px.bar(df.groupby("region")["sales"].sum().reset_index(),
                x="region", y="sales", title="Sales by Region",
                color_discrete_sequence=["#7c6ef7","#f97316","#a855f7","#fb923c"])
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if "category" in df.columns and "profit" in df.columns:
            fig = px.pie(df.groupby("category")["profit"].sum().reset_index(),
                names="category", values="profit", title="Profit by Category",
                color_discrete_sequence=["#7c6ef7","#f97316","#a855f7","#fb923c"])
            st.plotly_chart(fig, use_container_width=True)

    if "order_date" in df.columns and "sales" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        trend = df.groupby(df["order_date"].dt.date)["sales"].sum().reset_index()
        fig = px.line(trend, x="order_date", y="sales", title="Sales Trend",
            color_discrete_sequence=["#f97316"])
        st.plotly_chart(fig, use_container_width=True)

    product_col = next((c for c in ["product_name","product","item","name"] if c in df.columns), None)
    if product_col and "sales" in df.columns:
        top5 = df.groupby(product_col)["sales"].sum().nlargest(5).reset_index()
        fig = px.bar(top5, x="sales", y=product_col, orientation="h",
            title="Top 5 Products", color_discrete_sequence=["#7c6ef7"])
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🤖 AI Insight")
    if st.button("Generate Insights"):
        with st.spinner("Analyzing..."):
            try:
                sample = df.head(10).fillna("N/A").to_string(index=False)
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(f"Analyze this data and give 4 insights:\n{sample}")
                st.success(response.text)
            except Exception as e:
                st.error(f"Error: {e}")

    st.subheader("📋 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

else:
    st.info("👆 Upload a CSV file to get started!")
