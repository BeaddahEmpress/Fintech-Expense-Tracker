#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# ---------- Page config ----------
st.set_page_config(
    page_title="Fintech Expense Tracker",
    layout="wide"
)

# ---------- Color palette ----------
PRIMARY = "#0F4C81"      # deep blue
ACCENT = "#00B894"       # teal/green
GOLD = "#F5B700"         # gold accent
PALETTE = ["#0F4C81", "#00B894", "#F5B700", "#E84855", "#7A5CFA", "#3ABEFF", "#FF8552"]

# ---------- Custom CSS ----------
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #F7F9FC;
    }}
    h1, h2, h3 {{
        color: {PRIMARY};
    }}
    div[data-testid="stMetric"] {{
        background-color: white;
        border: 1px solid #E3E8EF;
        border-left: 5px solid {ACCENT};
        border-radius: 10px;
        padding: 15px 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }}
    div[data-testid="stMetricValue"] {{
        color: {PRIMARY};
    }}
    .stButton>button, .stDownloadButton>button {{
        background-color: {ACCENT};
        color: white;
        border-radius: 8px;
        border: none;
    }}
    .stButton>button:hover, .stDownloadButton>button:hover {{
        background-color: {PRIMARY};
        color: white;
    }}
    </style>
""", unsafe_allow_html=True)

# ---------- Supabase connection ----------
url = "https://ltzghyyhqglwqcwusmlt.supabase.co"
key = "sb_publishable_o-FY0g6pPRvMD4RySMY4tA_f6L_Rbxp"

supabase = create_client(url, key)

response = supabase.table("transactions").select("*").execute()
df = pd.DataFrame(response.data)

# ---------- Title ----------
st.title("Fintech Expense Tracker")
st.caption("A quick, colorful view of your spending habits")

# ---------- Top metrics ----------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Transactions", len(df))

with col2:
    st.metric("Highest Transaction", f"R{df['amount'].max():,.2f}")

with col3:
    st.metric("Average Transaction", f"R{df['amount'].mean():,.2f}")

with col4:
    highest_category = df.groupby("category")["amount"].sum().idxmax()
    st.metric("Highest Spending Category", highest_category)

st.metric("Total Spending", f"R{df['amount'].sum():,.2f}")

st.divider()

# ---------- Spending by category ----------
st.subheader("Spending by Category")

category_spending = df.groupby("category")["amount"].sum().sort_values(ascending=False)
cat_df = category_spending.reset_index()

bar_fig = px.bar(
    cat_df,
    x="category",
    y="amount",
    color="category",
    color_discrete_sequence=PALETTE,
    text_auto=".2s"
)
bar_fig.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
st.plotly_chart(bar_fig, use_container_width=True)

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Top 5 Spending Categories")
    st.dataframe(category_spending.head(5).reset_index().style.format({"amount": "R{:,.2f}"}).background_gradient(
        cmap="Blues", subset=["amount"]
    ))

with col_b:
    st.subheader("Category Spending Summary")
    st.dataframe(category_spending.reset_index().style.format({"amount": "R{:,.2f}"}).background_gradient(
        cmap="Blues", subset=["amount"]
    ))

st.subheader("Spending Distribution")

pie_data = category_spending.reset_index()
fig = px.pie(
    pie_data,
    names="category",
    values="amount",
    title="Spending Distribution by Category",
    color_discrete_sequence=PALETTE,
    hole=0.4
)
fig.update_traces(textposition="inside", textinfo="percent+label")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------- Filter transactions ----------
st.subheader("Filter Transactions")

selected_date = st.date_input(
    "Choose a date",
    value=(df["transaction_date"].min(), df["transaction_date"].max())
)

selected_category = st.selectbox(
    "Choose a category",
    ["All"] + sorted(df["category"].unique().tolist())
)

if selected_category == "All":
    filtered_df = df
else:
    filtered_df = df[df["category"] == selected_category]

if isinstance(selected_date, tuple):
    start_date = pd.to_datetime(selected_date[0])
    end_date = pd.to_datetime(selected_date[1])

    transaction_dates = pd.to_datetime(filtered_df["transaction_date"])

    filtered_df = filtered_df[
        (transaction_dates >= start_date) & (transaction_dates <= end_date)
    ]

filtered_total = filtered_df["amount"].sum()

st.metric("Selected Category Spending", f"R{filtered_total:,.2f}")
st.dataframe(filtered_df)

st.divider()

# ---------- Spending over time ----------
st.subheader("Spending Over Time")

df["transaction_date"] = pd.to_datetime(df["transaction_date"])
daily_spending = df.groupby("transaction_date")["amount"].sum().reset_index()

line_fig = px.line(
    daily_spending,
    x="transaction_date",
    y="amount",
    markers=True,
    color_discrete_sequence=[ACCENT]
)
line_fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
st.plotly_chart(line_fig, use_container_width=True)

st.subheader("Monthly Spending Trend")

monthly_spending = df.groupby(df["transaction_date"].dt.to_period("M"))["amount"].sum().reset_index()
monthly_spending["transaction_date"] = monthly_spending["transaction_date"].astype(str)

monthly_fig = px.line(
    monthly_spending,
    x="transaction_date",
    y="amount",
    markers=True,
    color_discrete_sequence=[GOLD]
)
monthly_fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
st.plotly_chart(monthly_fig, use_container_width=True)

st.divider()

# ---------- Full table + download ----------
st.subheader("Your Transaction Data")
st.dataframe(df)

st.download_button(
    "Download Transactions",
    filtered_df.to_csv(index=False),
    "filtered_transactions.csv",
    "text/csv"
)

