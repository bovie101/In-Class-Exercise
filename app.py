import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Sales Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {padding-top: 1.2rem; padding-bottom: 1.2rem;}
        div[data-testid="metric-container"] {
            background: rgba(250,250,250,0.9);
            border: 1px solid rgba(49, 51, 63, 0.15);
            padding: 14px 16px;
            border-radius: 14px;
        }
        .small-note {
            font-size: 0.9rem;
            color: #6b7280;
            margin-top: -0.35rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data():
    orders = pd.read_csv("orders.csv")
    returns = pd.read_csv("returns.csv")
    customers = pd.read_csv("customers.csv")

    orders["Order Date"] = pd.to_datetime(orders["Order Date"], errors="coerce")
    orders["Ship Date"] = pd.to_datetime(orders["Ship Date"], errors="coerce")

    returns = returns.copy()
    returns["Returned Flag"] = returns["Returned"].fillna("").str.strip().str.lower().eq("yes")

    df = (
        orders.merge(customers, on="Customer ID", how="left")
        .merge(returns[["Order ID", "Returned Flag"]], on="Order ID", how="left")
    )

    df["Returned Flag"] = df["Returned Flag"].fillna(False)
    df["Returned Orders"] = df["Order ID"].where(df["Returned Flag"])
    df["Order Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    df["Profit Margin %"] = (df["Profit"] / df["Sales"]).replace([pd.NA, pd.NaT, float("inf"), -float("inf")], 0.0)
    df["Profit Margin %"] = df["Profit Margin %"].fillna(0.0)

    numeric_cols = ["Sales", "Quantity", "Discount", "Profit"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    return df


def currency(value: float) -> str:
    return f"${value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.1%}"


df = load_data()

if df.empty:
    st.error("No data available.")
    st.stop()

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

with st.sidebar:
    st.title("Filters")

    region_options = sorted([x for x in df["Region"].dropna().unique()])
    selected_regions = st.multiselect(
        "Region",
        options=region_options,
        default=region_options,
        help="Filter dashboard metrics and charts by region.",
    )

    category_options = sorted([x for x in df["Category"].dropna().unique()])
    selected_categories = st.multiselect(
        "Category",
        options=category_options,
        default=category_options,
        help="Filter dashboard metrics and charts by category.",
    )

    date_range = st.date_input(
        "Order Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Select the order date window.",
    )

    st.markdown("---")
    st.caption("The dashboard updates all metrics and charts instantly based on the selected filters.")


filtered = df.copy()

if selected_regions:
    filtered = filtered[filtered["Region"].isin(selected_regions)]
else:
    filtered = filtered.iloc[0:0]

if selected_categories:
    filtered = filtered[filtered["Category"].isin(selected_categories)]
else:
    filtered = filtered.iloc[0:0]

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[filtered["Order Date"].between(start_date, end_date)]

st.title("📊 Sales Performance Dashboard")
st.markdown(
    '<div class="small-note">Interactive Streamlit dashboard using Plotly charts, sidebar filters, and merged orders / returns / customers data.</div>',
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("No records match the current filters. Adjust the sidebar selections.")
    st.stop()

unique_order_count = filtered["Order ID"].nunique()
returned_order_count = filtered.loc[filtered["Returned Flag"], "Order ID"].nunique()
total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
profit_margin = 0 if total_sales == 0 else total_profit / total_sales

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Sales", currency(total_sales))
m2.metric("Total Profit", currency(total_profit))
m3.metric("Returned Orders", f"{returned_order_count:,}")
m4.metric("Profit Margin", pct(profit_margin))

trend = (
    filtered.groupby("Order Month", as_index=False)[["Sales", "Profit"]]
    .sum()
    .sort_values("Order Month")
)
fig_trend = px.line(
    trend,
    x="Order Month",
    y=["Sales", "Profit"],
    markers=True,
    title="Monthly Sales and Profit Trend",
    labels={"value": "Amount", "Order Month": "Month", "variable": "Metric"},
)
fig_trend.update_layout(legend_title_text="", hovermode="x unified")

top_subcats = (
    filtered.groupby("Sub-Category", as_index=False)["Sales"]
    .sum()
    .sort_values("Sales", ascending=False)
    .head(10)
)
fig_subcats = px.bar(
    top_subcats,
    x="Sales",
    y="Sub-Category",
    orientation="h",
    title="Top 10 Sub-Categories by Sales",
    text_auto=".2s",
)
fig_subcats.update_layout(yaxis={"categoryorder": "total ascending"})

region_summary = (
    filtered.groupby("Region", as_index=False)[["Sales", "Profit"]]
    .sum()
    .sort_values("Sales", ascending=False)
)
region_long = region_summary.melt(
    id_vars="Region",
    value_vars=["Sales", "Profit"],
    var_name="Metric",
    value_name="Amount",
)
fig_region = px.bar(
    region_long,
    x="Region",
    y="Amount",
    color="Metric",
    barmode="group",
    title="Sales vs Profit by Region",
    text_auto=".2s",
)

scatter = filtered.copy()
scatter["Returned"] = scatter["Returned Flag"].map({True: "Returned", False: "Not Returned"})
fig_scatter = px.scatter(
    scatter,
    x="Discount",
    y="Profit",
    size="Sales",
    color="Category",
    symbol="Returned",
    hover_data={
        "Product Name": True,
        "Sub-Category": True,
        "Region": True,
        "Sales": ":,.2f",
        "Profit": ":,.2f",
        "Discount": ":.0%",
        "Order ID": True,
    },
    title="Discount vs Profit",
)
fig_scatter.update_traces(marker=dict(sizemode="area"))

seg_summary = (
    filtered.groupby("Segment", as_index=False)[["Sales", "Profit"]]
    .sum()
    .sort_values("Sales", ascending=False)
)
fig_segment = px.bar(
    seg_summary,
    x="Segment",
    y=["Sales", "Profit"],
    barmode="group",
    title="Sales and Profit by Customer Segment",
    labels={"value": "Amount", "variable": "Metric"},
)

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(fig_trend, use_container_width=True)
with c2:
    st.plotly_chart(fig_subcats, use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.plotly_chart(fig_region, use_container_width=True)
with c4:
    st.plotly_chart(fig_segment, use_container_width=True)

st.plotly_chart(fig_scatter, use_container_width=True)

with st.expander("View filtered data"):
    st.dataframe(
        filtered[
            [
                "Order ID",
                "Order Date",
                "Customer ID",
                "Region",
                "Category",
                "Sub-Category",
                "Product Name",
                "Sales",
                "Quantity",
                "Discount",
                "Profit",
                "Returned Flag",
            ]
        ].sort_values("Order Date", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download filtered data as CSV",
    data=csv_data,
    file_name="filtered_sales_data.csv",
    mime="text/csv",
)

st.caption(
    f"Showing {len(filtered):,} line items across {unique_order_count:,} orders "
    f"from {filtered['Order Date'].min().date()} to {filtered['Order Date'].max().date()}."
)
