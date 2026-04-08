# Sales Dashboard Streamlit App

## Overview
This project is a Streamlit dashboard for exploring the provided sales data with Plotly visualizations and sidebar filters.

## Features
- Plotly charts with built-in interactivity
- Sidebar filters for Region, Category, and Date Range
- KPI cards for Total Sales, Total Profit, Unique Orders, and Return Rate
- Filtered data preview table
- Automatic loading of `orders.csv`, `customers.csv`, and `returns.csv` from the same folder as the app

## Required Files
Keep these files in the same directory:
- `streamlit_sales_app.py`
- `requirements.txt`
- `orders.csv`
- `customers.csv`
- `returns.csv`

## Install
```bash
pip install -r requirements.txt
```

## Run
```bash
streamlit run streamlit_sales_app.py
```

## Notes
- The app merges `orders.csv` and `customers.csv` on `Customer ID`
- The app merges `returns.csv` on `Order ID`
- If any CSV file is missing, the app shows a clear error message
- These dependency versions are chosen to work better with newer Python environments, including Python 3.14
