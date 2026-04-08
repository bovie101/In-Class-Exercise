
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sales Analysis Dashboard", page_icon="📊", layout="wide")

DATA_DIR = Path(__file__).resolve().parent
ORDERS_PATH = DATA_DIR / "orders.csv"
CUSTOMERS_PATH = DATA_DIR / "customers.csv"
RETURNS_PATH = DATA_DIR / "returns.csv"


@st.cache_data
def load_data():
    orders = pd.read_csv(ORDERS_PATH)
    customers = pd.read_csv(CUSTOMERS_PATH)
    returns = pd.read_csv(RETURNS_PATH)

    orders["Order Date"] = pd.to_datetime(orders["Order Date"], format="%m/%d/%y", errors="coerce")
    orders["Ship Date"] = pd.to_datetime(orders["Ship Date"], format="%m/%d/%y", errors="coerce")

    df = orders.merge(customers, on="Customer ID", how="left")
    df = df.merge(returns, on="Order ID", how="left")
    df["Returned"] = df["Returned"].fillna("No")
    df["Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()

    return df


df = load_data()

st.title("📊 Sales Analysis Dashboard")
st.caption("Interactive Streamlit app using Plotly charts and sidebar filters.")

with st.sidebar:
    st.header("Filters")

    all_regions = sorted(df["Region"].dropna().unique().tolist())
    selected_regions = st.multiselect(
        "Region",
        options=all_regions,
        default=all_regions,
    )

    all_categories = sorted(df["Category"].dropna().unique().tolist())
    selected_categories = st.multiselect(
        "Category",
        options=all_categories,
        default=all_categories,
    )

    min_date = df["Order Date"].min().date()
    max_date = df["Order Date"].max().date()
    selected_dates = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date, end_date = min_date, max_date

filtered = df.copy()

if selected_regions:
    filtered = filtered[filtered["Region"].isin(selected_regions)]

if selected_categories:
    filtered = filtered[filtered["Category"].isin(selected_categories)]

filtered = filtered[
    filtered["Order Date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))
]

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
total_orders = filtered["Order ID"].nunique()
return_rate = (filtered["Returned"].eq("Yes").mean()) * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sales", f"${total_sales:,.2f}")
c2.metric("Total Profit", f"${total_profit:,.2f}")
c3.metric("Unique Orders", f"{total_orders:,}")
c4.metric("Return Rate", f"{return_rate:.1f}%")

monthly_sales = (
    filtered.groupby("Month", as_index=False)["Sales"]
    .sum()
    .sort_values("Month")
)

sales_by_region = (
    filtered.groupby("Region", as_index=False)["Sales"]
    .sum()
    .sort_values("Sales", ascending=False)
)

profit_by_category = (
    filtered.groupby("Category", as_index=False)["Profit"]
    .sum()
    .sort_values("Profit", ascending=False)
)

sales_by_subcategory = (
    filtered.groupby("Sub-Category", as_index=False)["Sales"]
    .sum()
    .sort_values("Sales", ascending=False)
)

fig_monthly_sales = px.line(
    monthly_sales,
    x="Month",
    y="Sales",
    markers=True,
    title="Monthly Sales Over Time",
)

fig_profit_box = px.box(
    filtered,
    x="Category",
    y="Profit",
    points="outliers",
    title="Profit Distribution by Category",
)

fig_region_sales = px.bar(
    sales_by_region,
    x="Region",
    y="Sales",
    title="Total Sales by Region",
)

fig_subcategory_sales = px.bar(
    sales_by_subcategory,
    x="Sub-Category",
    y="Sales",
    title="Total Sales by Sub-Category",
)

fig_scatter = px.scatter(
    filtered,
    x="Sales",
    y="Profit",
    color="Category",
    hover_data=["Order ID", "Product Name", "Region", "Segment"],
    title="Sales vs Profit",
)

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.plotly_chart(fig_monthly_sales, use_container_width=True)
with row1_col2:
    st.plotly_chart(fig_region_sales, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    st.plotly_chart(fig_profit_box, use_container_width=True)
with row2_col2:
    st.plotly_chart(fig_subcategory_sales, use_container_width=True)

st.plotly_chart(fig_scatter, use_container_width=True)

with st.expander("Preview filtered data"):
    st.dataframe(
        filtered[
            [
                "Order ID",
                "Order Date",
                "Customer ID",
                "Region",
                "Category",
                "Sub-Category",
                "Sales",
                "Profit",
                "Returned",
            ]
        ].sort_values(["Order Date", "Order ID"], ascending=[False, True]),
        use_container_width=True,
        height=350,
    )
