import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# Supabase connection
url = "https://ltzghyyhqglwqcwusmlt.supabase.co"
key = "sb_publishable_o-FY0g6pPRvMD4RySMY4tA_f6L_Rbxp"

supabase = create_client(url, key)

# Get transactions
response = supabase.table("transactions").select("*").execute()

# Convert Supabase data into a Pandas Dataframe
df = pd.DataFrame(response.data)

# Page title
st.title("Fintech Expense Tracker")

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

st.subheader("Spending by Category")

category_spending = df.groupby("category")["amount"].sum().sort_values(ascending=False)

st.bar_chart(category_spending)
st.subheader("Top 5 Spending Categories")

st.dataframe(category_spending.head(5))

st.subheader("Category Spending Summary")

st.dataframe(category_spending)

st.subheader("Spending Distribution")

pie_data = category_spending.reset_index()

fig = px.pie(pie_data, names="category", values="amount", title="Spending Distribution by Category")

st.plotly_chart(fig, use_container_width=True)

category_spending = (df.groupby("category"))
st.subheader("Filter Transactions")
selected_date = st.date_input("Choose a date", value=(df["transaction_date"].min(), df["transaction_date"].max()))

# Filter Transactions
selected_category = st.selectbox("Choose a category",["All"] + sorted(df["category"].unique().tolist()))

if selected_category == "All":
	filtered_df = df
else:
	filtered_df = df[df["category"] == selected_category]
if isinstance(selected_date,tuple):
	start_date = pd.to_datetime(selected_date[0])
	end_date = pd.to_datetime(selected_date[1])

	transaction_dates = pd.to_datetime(filtered_df["transaction_date"])
	
	filtered_df = filtered_df[(transaction_dates >= start_date)
	& (transaction_dates <= end_date)]
	

filtered_total = filtered_df["amount"].sum()

st.metric("Selected Category Spending",f"R{filtered_total:,.2f}")

st.dataframe(filtered_df)

st.subheader("Spending Over Time")

df["transaction_date"] = pd.to_datetime(df["transaction_date"])

daily_spending = df.groupby("transaction_date")["amount"].sum()

st.line_chart(daily_spending)
st.subheader("Monthly Spending Trend")

monthly_spending = (df.groupby(df["transaction_date"].dt.to_period("M"))["amount"].sum())

monthly_spending.index = (monthly_spending.index.astype(str))

st.line_chart(monthly_spending)

# Display transactions
st.write("Your transaction data")

st.dataframe(df)
st.download_button("Download Transactions", filtered_df.to_csv(index=False), "filtered_transactions.csv", "text/csv")