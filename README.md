# Sales Dashboard Streamlit App

## Overview

This project is an interactive data analysis dashboard built using
Streamlit and Plotly. It allows users to explore sales, profit, and
customer data with dynamic filters and visualizations.

## Features

-   Interactive Plotly charts\
-   Sidebar filters for Region, Category, and Date Range\
-   KPIs for Sales, Profit, Orders, and Return Rate\
-   Data preview table

## Requirements

Install dependencies using:

``` bash
pip install -r requirements.txt
```

## How to Run

Make sure the following CSV files are in the same directory: -
orders.csv\
- customers.csv\
- returns.csv

Then run the app:

``` bash
streamlit run streamlit_sales_app.py
```

## File Structure

    streamlit_sales_app.py  
    requirements.txt  
    orders.csv  
    customers.csv  
    returns.csv  

## Notes

-   Ensure Python version is 3.9 or higher\
-   If deployment fails, verify file paths and dependencies
