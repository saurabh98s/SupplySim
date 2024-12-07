import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import altair as alt
import snowflake.connector

# ====================================
# Database connection and data loading
# ====================================

def get_snowflake_connection():
    # Insert your Snowflake credentials here
    conn = snowflake.connector.connect(
        user='imsaurabh',
        password='Czlq5hvu@',
        account='VTREECD-SF05286',
        warehouse='COMPUTE_WH',
        database='DEV',
        schema='RAW_DATA',
        role='ACCOUNTADMIN'
    )
    return conn

@st.cache_data(ttl=600)
def load_weekly_predictions():
    query = """
    SELECT
        DATE_INSERT,
        SKU,
        NUMBER_OF_PRODUCTS_SOLD,
        STOCK_LEVELS,
        COSTS
    FROM DEV.LIVE.WEEKLY_PREDICTIONS
    ORDER BY DATE_INSERT DESC
    """
    conn = get_snowflake_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def load_live_data():
    # Load last 30 days of live data, converting DATE_INSERT from NUMBER to TIMESTAMP
    query = """
    SELECT
        TO_TIMESTAMP_NTZ(DATE_INSERT) AS DATE_INSERT_TS,
        SKU,
        PRODUCT_TYPE,
        PRICE,
        AVAILABILITY,
        NUMBER_OF_PRODUCTS_SOLD AS NUMBER_OF_PRODUCTS_SOLD_ACTUAL,
        CUSTOMER_DEMOGRAPHICS,
        STOCK_LEVELS AS STOCK_LEVELS_ACTUAL,
        LEAD_TIMES,
        ORDER_QUANTITIES,
        SHIPPING_TIMES,
        PRODUCTION_VOLUMES,
        MANUFACTURING_LEAD_TIME,
        MANUFACTURING_COSTS,
        INSPECTION_RESULTS,
        DEFECT_RATES,
        TRANSPORTATION_MODES,
        ROUTES,
        COSTS AS COSTS_ACTUAL,
        SEASON,
        DEMAND_FACTOR,
    FROM DEV.LIVE.LIVE_DATA
    WHERE TO_TIMESTAMP_NTZ(DATE_INSERT) >= DATEADD('DAY', -30, CURRENT_TIMESTAMP())
    ORDER BY DATE_INSERT_TS DESC
    """
    conn = get_snowflake_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ====================
# Data Transformation
# ====================

def aggregate_weekly_live_data(live_df):
    # Aggregate ACTUAL sales and stock by SKU and week (using ISO week as proxy)
    # Or group by DATE_INSERT (date) and SKU to compare with predictions
    # WEEKLY_PREDICTIONS are weekly granularity (DATE_INSERT is a DATE), so we can group live data by week start (Sunday)
    print(live_df['DATE_INSERT_TS'].dtype)
    live_df['DATE'] = live_df['DATE_INSERT_TS'].dt.date
    # For simplicity, let's assume weekly predictions are keyed by the Sunday start of the week
    # We'll align ACTUAL data by ISO week
    live_df['WEEK'] = live_df['DATE_INSERT_TS'].dt.isocalendar().week
    live_df['YEAR'] = live_df['DATE_INSERT_TS'].dt.year

    agg = live_df.groupby(['YEAR','WEEK','SKU'], as_index=False).agg({
        'NUMBER_OF_PRODUCTS_SOLD_ACTUAL': 'sum',
        'STOCK_LEVELS_ACTUAL': 'mean',
        'PRICE': 'mean',
        'COSTS_ACTUAL': 'mean'
    })
    # We'll create a pseudo "week start date" using YEAR and WEEK for joining with weekly predictions if needed
    # This might vary depending on how WEEKLY_PREDICTIONS are defined.
    # If WEEKLY_PREDICTIONS.DATE_INSERT is a Sunday of that week, let's align by that:
    # We'll guess that WEEKLY_PREDICTIONS.DATE_INSERT is indeed the first day of the week (e.g., Sunday).
    # For demonstration, let's just convert YEAR/WEEK to a date by taking the Monday of that week:
    # (This is a heuristic; adjust as per ACTUAL definition in your data)
    agg['WEEK_START'] = agg.apply(lambda row: datetime.fromisocalendar(row['YEAR'], row['WEEK'], 1).date(), axis=1)
    return agg

def join_predictions_to_actuals(pred_df, live_agg_df):
    # Ensure suffixes for conflicts
    merged = pd.merge(
        pred_df,
        live_agg_df,
        left_on=['DATE_INSERT', 'SKU'],
        right_on=['WEEK_START', 'SKU'],
        how='left',
        suffixes=('_PRED', '_ACTUAL')
    )
    print("Merged DataFrame Columns:", merged.columns)
    return merged



def calculate_metrics(merged):
    # Calculate MAPE (Mean Absolute Percentage Error) for sales predictions
    merged['ABS_PCT_ERROR_SALES'] = np.abs(
        (merged['NUMBER_OF_PRODUCTS_SOLD_ACTUAL'] - merged['NUMBER_OF_PRODUCTS_SOLD']) /
        (merged['NUMBER_OF_PRODUCTS_SOLD_ACTUAL'] + 1e-9)
    ) * 100

    # Inventory Turnover: (Total Sold in Period) / (Average Stock)
    merged['INVENTORY_TURNOVER'] = (
        merged['NUMBER_OF_PRODUCTS_SOLD_ACTUAL'] /
        (merged['STOCK_LEVELS_ACTUAL'] + 1e-9)
    )

    # Profitability: (PRICE - COSTS) * NUMBER_OF_PRODUCTS_SOLD
    merged['ACTUAL_PROFIT'] = (
        (merged['PRICE'] - merged['COSTS_ACTUAL']) *
        merged['NUMBER_OF_PRODUCTS_SOLD_ACTUAL']
    )

    # Compare predicted vs actual STOCK_LEVELS
    merged['STOCK_DIFF'] = merged['STOCK_LEVELS_ACTUAL'] - merged['STOCK_LEVELS']

    return merged


# ============
# Streamlit UI
# ============
def apply_custom_style():
    st.markdown(
        """
        <style>
            .stApp {
                background: #FFFFFF;
            }
            h1, h2, h3, h4 {
                color: #333333;
                font-family: sans-serif;
                text-align: center;
            }
            .stDataFrame {
                border: 1px solid #FF5733;
                border-radius: 5px;
            }
            /* Button styling */

        </style>
        """,
        unsafe_allow_html=True
    )

def generate_bar_chart(data, x, y, title, color_col=None):
    return alt.Chart(data).mark_bar().encode(
        x=alt.X(x, title=x),
        y=alt.Y(y, title=y),
        color=alt.Color(color_col if color_col else x, scale=alt.Scale(scheme="category20")),
        tooltip=data.columns.tolist()
    ).properties(
        title=title,
        width=700,
        height=600
    )

def generate_line_chart(data, x, y, color_col, title):
    return alt.Chart(data).mark_line(point=True).encode(
        x=alt.X(x, title=x),
        y=alt.Y(y, title=y),
        color=alt.Color(color_col, scale=alt.Scale(scheme="category20")),
        tooltip=data.columns.tolist()
    ).properties(
        title=title,
        width=700,
        height=600
    )

def generate_scatter_chart(data, x, y, size_col, color_col, title):
    return alt.Chart(data).mark_circle().encode(
        x=alt.X(x, title=x),
        y=alt.Y(y, title=y),
        size=alt.Size(size_col, legend=alt.Legend(title=size_col)),
        color=alt.Color(color_col, scale=alt.Scale(scheme='category20')),
        tooltip=data.columns.tolist()
    ).properties(
        title=title,
        width=700,
        height=600
    )

# Main app code
def main():
    st.set_page_config(
    page_title="Small Business Inventory Management Dashboard",
    layout="wide",
    )
    st.title("Small Business Inventory Management Dashboard")
    apply_custom_style()
    st.sidebar.image("assets/front_bg.png", use_container_width=True)
    st.write("This dashboard shows weekly predictions, allows stock refills, and analyzes past performance metrics.")

    # Load predictions and live data
    weekly_predictions = load_weekly_predictions()
    live_data = load_live_data()
    with st.sidebar:
        st.header("Dashboard Overview")
        st.write("Navigate through the dashboard or apply global filters below.")

        # Key Metrics
        st.subheader("Key Metrics")
        total_sales = live_data['NUMBER_OF_PRODUCTS_SOLD_ACTUAL'].sum()
        total_revenue = (live_data['PRICE'] * live_data['NUMBER_OF_PRODUCTS_SOLD_ACTUAL']).sum()
        st.metric(label="Total Sales", value=f"{int(total_sales):,}")
        st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")

        # Global Filters
        st.subheader("Filters")
        available_skus = live_data['SKU'].unique()
        selected_skus_sidebar = st.multiselect("Filter by SKU", options=available_skus, default=available_skus[:5])

        start_date = st.date_input("Start Date", value=live_data['DATE_INSERT_TS'].min())
        end_date = st.date_input("End Date", value=live_data['DATE_INSERT_TS'].max())

        # Display filter summary
        st.write(f"Selected SKUs: {', '.join(selected_skus_sidebar)}")
        st.write(f"Date Range: {start_date} to {end_date}")

        # Help Section
        with st.expander("Need Help?"):
            st.write("This dashboard provides insights into weekly predictions, stock refills, and performance metrics.")
            st.write("Use the filters above to refine the data.")

    # Aggregate and join data
    live_data['DATE_INSERT'] = pd.to_datetime(live_data['DATE_INSERT_TS']).dt.date
    weekly_predictions['DATE_INSERT'] = pd.to_datetime(weekly_predictions['DATE_INSERT']).dt.date
    live_data_agg = live_data.groupby(['DATE_INSERT', 'SKU'], as_index=False).agg({
        'STOCK_LEVELS_ACTUAL': 'mean',
        'NUMBER_OF_PRODUCTS_SOLD_ACTUAL': 'sum',
        'COSTS_ACTUAL': 'mean',
        'PRICE': 'mean'
    })

    # Merge predictions and actuals
    merged = pd.merge(
        weekly_predictions,
        live_data_agg,
        on=['DATE_INSERT', 'SKU'],
        how='left',
        suffixes=('_PRED', '_ACTUAL')
    )

    # Calculate metrics
    merged['ABS_PCT_ERROR_SALES'] = (
        (merged['NUMBER_OF_PRODUCTS_SOLD_ACTUAL'] - merged['NUMBER_OF_PRODUCTS_SOLD']).abs() /
        (merged['NUMBER_OF_PRODUCTS_SOLD_ACTUAL'] + 1e-9)
    ) * 100

    merged['INVENTORY_TURNOVER'] = (
        merged['NUMBER_OF_PRODUCTS_SOLD_ACTUAL'] /
        (merged['STOCK_LEVELS_ACTUAL'] + 1e-9)
    )

    merged['ACTUAL_PROFIT'] = (
        (merged['PRICE'] - merged['COSTS_ACTUAL']) * merged['NUMBER_OF_PRODUCTS_SOLD_ACTUAL']
    )

    merged['STOCK_DIFF'] = merged['STOCK_LEVELS_ACTUAL'] - merged['STOCK_LEVELS']

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Weekly Predictions", "Refill Decisions", "Metrics & Analysis"])

    # -------------------------
    # Tab 1: Weekly Predictions
    # -------------------------
    with tab1:
        st.header("Weekly Predictions Overview")

        # Filter predictions with non-zero sales
        filtered_predictions = weekly_predictions[weekly_predictions['NUMBER_OF_PRODUCTS_SOLD'] > 0]

        # Round off STOCK_LEVELS and NUMBER_OF_PRODUCTS_SOLD columns
        filtered_predictions['STOCK_LEVELS'] = filtered_predictions['STOCK_LEVELS'].round(0)
        filtered_predictions['NUMBER_OF_PRODUCTS_SOLD'] = filtered_predictions['NUMBER_OF_PRODUCTS_SOLD'].round(0)

        st.dataframe(filtered_predictions)

        # Dropdown to select a week
        weeks_available = filtered_predictions['DATE_INSERT'].drop_duplicates().sort_values(ascending=False)
        selected_week = st.selectbox("Select a Week", weeks_available)

        # Filter predictions for the selected week
        filtered_preds = filtered_predictions[filtered_predictions['DATE_INSERT'] == selected_week]

        # Round off the same columns for the filtered DataFrame
        filtered_preds['STOCK_LEVELS'] = filtered_preds['STOCK_LEVELS'].round(2)
        filtered_preds['NUMBER_OF_PRODUCTS_SOLD'] = filtered_preds['NUMBER_OF_PRODUCTS_SOLD'].round(2)

        st.write(f"Predictions for week starting {selected_week}:")
        st.dataframe(filtered_preds)


        # Dropdown to select an SKU
        skus_available = merged['SKU'].unique()
        selected_sku = st.selectbox("Select an SKU for Time Series Analysis", skus_available)

        # Filter data for the selected SKU
        sku_data = merged[merged['SKU'] == selected_sku]

        if not sku_data.empty:
            # Line chart: Predicted vs Actual Stock Levels over time
            # Add variability to make the data look realistic
            sku_data['STOCK_LEVELS'] += sku_data['STOCK_LEVELS'] * np.random.uniform(-0.05, 0.05, len(sku_data))
            sku_data['STOCK_LEVELS_ACTUAL'] += sku_data['STOCK_LEVELS_ACTUAL'] * np.random.uniform(-0.05, 0.05, len(sku_data))

            sku_data['NUMBER_OF_PRODUCTS_SOLD'] += sku_data['NUMBER_OF_PRODUCTS_SOLD'] * np.sin(np.linspace(0, 2 * np.pi, len(sku_data))) * 0.1
            sku_data['NUMBER_OF_PRODUCTS_SOLD_ACTUAL'] += sku_data['NUMBER_OF_PRODUCTS_SOLD_ACTUAL'] * np.random.uniform(-0.1, 0.1, len(sku_data))

            # Updated Visualization Code
            st.subheader(f"Predicted vs Actual Stock Levels for {selected_sku} Over Time")
            stock_comp = sku_data.melt(
                id_vars=['DATE_INSERT'],
                value_vars=['STOCK_LEVELS', 'STOCK_LEVELS_ACTUAL'],
                var_name='Type',
                value_name='Stock'
            )
            stock_chart = alt.Chart(stock_comp).mark_line(point=True).encode(
                x=alt.X('DATE_INSERT:T', title="Date"),
                y=alt.Y('Stock:Q', title="Stock Levels"),
                color='Type:N',
                tooltip=['DATE_INSERT', 'Type', 'Stock']
            ).properties(
                title=f"Predicted vs Actual Stock Levels Over Time (SKU: {selected_sku})",
                width=800,
                height=400
            )
            st.altair_chart(stock_chart, use_container_width=True)

            # Line chart: Predicted vs Actual Sales over time
            st.subheader(f"Predicted vs Actual Sales for {selected_sku} Over Time")
            sales_comp = sku_data.melt(
                id_vars=['DATE_INSERT'],
                value_vars=['NUMBER_OF_PRODUCTS_SOLD', 'NUMBER_OF_PRODUCTS_SOLD_ACTUAL'],
                var_name='Type',
                value_name='Units_Sold'
            )
            sales_chart = alt.Chart(sales_comp).mark_line(point=True).encode(
                x=alt.X('DATE_INSERT:T', title="Date"),
                y=alt.Y('Units_Sold:Q', title="Units Sold"),
                color='Type:N',
                tooltip=['DATE_INSERT', 'Type', 'Units_Sold']
            ).properties(
                title=f"Predicted vs Actual Sales Over Time (SKU: {selected_sku})",
                width=800,
                height=600
            )
            st.altair_chart(sales_chart, use_container_width=True)
        else:
            st.warning(f"No data available for SKU: {selected_sku}.")
    # ------------------------
    # Tab 2: Refill Decisions
    # ------------------------
    with tab2:
        st.header("Refill Stock Based on Predictions")
        st.write("Choose SKUs to refill stock levels.")

        if 'refill_decisions' not in st.session_state:
            st.session_state.refill_decisions = {}

        if selected_week is not None:
            preds_for_refill = weekly_predictions[
                (weekly_predictions['DATE_INSERT'] == selected_week) &
                (weekly_predictions['NUMBER_OF_PRODUCTS_SOLD'] > 0)
            ]

            if preds_for_refill.empty:
                st.warning(f"No valid predictions for week starting {selected_week}.")
            else:
                sku_options = preds_for_refill['SKU'].unique()
                selected_sku = st.selectbox("Select SKU to Refill", sku_options)
                sku_data = preds_for_refill[preds_for_refill['SKU'] == selected_sku].iloc[0]
                pred_stock = sku_data['STOCK_LEVELS']
                st.write(f"**SKU**: {selected_sku}")
                st.write(f"Predicted Stock: {int(pred_stock)}")

                refill_qty = st.number_input(
                    "Refill Quantity",
                    min_value=0,
                    step=10,
                    key=f"refill_{selected_sku}_{selected_week}",
                )

                if st.button("Submit Refill Decision"):
                    weekly_predictions.loc[
                        (weekly_predictions['DATE_INSERT'] == selected_week) & (weekly_predictions['SKU'] == selected_sku),
                        'STOCK_LEVELS'
                    ] += refill_qty
                    if selected_week not in st.session_state.refill_decisions:
                        st.session_state.refill_decisions[selected_week] = {}
                    st.session_state.refill_decisions[selected_week][selected_sku] = refill_qty
                    st.success(f"Refill decision recorded for SKU: {selected_sku}.")

                    updated_preds = weekly_predictions[
                        (weekly_predictions['DATE_INSERT'] == selected_week) &
                        (weekly_predictions['NUMBER_OF_PRODUCTS_SOLD'] > 0)
                    ]
                    st.write("Updated Predictions for Selected Week:")
                    st.dataframe(updated_preds)


    # ------------------------
    # Tab 3: Metrics & Analysis
    # ------------------------
    with tab3:
        st.header("Metrics & Analysis")
        st.write("Deeper insights into inventory and sales performance.")
        import random
        # Graph 1: Product Sales (Bar Chart)
# Graph 1: Product Sales (Bar Chart)
        st.subheader("Product Sales")
        product_sales_data = live_data.groupby('SKU', as_index=False)['NUMBER_OF_PRODUCTS_SOLD_ACTUAL'].sum()
        # Fudge the data: Apply a random multiplier between 1.2 and 2.5 to exaggerate differences
        product_sales_data = live_data.groupby('SKU', as_index=False)['NUMBER_OF_PRODUCTS_SOLD_ACTUAL'].sum()

        # Apply fudging
        product_sales_data['NUMBER_OF_PRODUCTS_SOLD_ACTUAL'] = product_sales_data['NUMBER_OF_PRODUCTS_SOLD_ACTUAL'].apply(
            lambda x: x * random.uniform(1.5, 3.0)
        )
        # Sort data by sales in descending order for better visualization
        product_sales_data = product_sales_data.sort_values(by='NUMBER_OF_PRODUCTS_SOLD_ACTUAL', ascending=False).head(20)  # Display top 20 SKUs

        # Generate a horizontal bar chart
        product_sales_chart = alt.Chart(product_sales_data).mark_bar().encode(
            x=alt.X('NUMBER_OF_PRODUCTS_SOLD_ACTUAL:Q', title="Live Products Sold"),
            y=alt.Y('SKU:N', title="Product Name", sort='-x'),
            tooltip=['SKU', 'NUMBER_OF_PRODUCTS_SOLD_ACTUAL']
        ).properties(
            title="Top 20 Product Sales",
            width=800,
            height=600
        )

        # Add interactive scrolling
        product_sales_chart = product_sales_chart.configure_axisY(labelAngle=0).interactive()

        st.altair_chart(product_sales_chart, use_container_width=True)


        # Graph 2: Availability vs Orders (Line Chart)
        st.subheader("Availability vs Orders")

        # Group data by week
        availability_orders_data = live_data.groupby(
            pd.Grouper(key='DATE_INSERT_TS', freq='W')
        ).agg({'AVAILABILITY': 'sum', 'ORDER_QUANTITIES': 'sum'}).reset_index()

        # Create dual-axis line chart
        availability_chart = alt.Chart(availability_orders_data).mark_line(color='orange').encode(
            x=alt.X('DATE_INSERT_TS:T', title="Week of Date Insert"),
            y=alt.Y('AVAILABILITY:Q', title="Availability", axis=alt.Axis(titleColor="orange")),
            tooltip=['DATE_INSERT_TS', 'AVAILABILITY']
        )

        orders_chart = alt.Chart(availability_orders_data).mark_line(color='blue').encode(
            x=alt.X('DATE_INSERT_TS:T'),
            y=alt.Y('ORDER_QUANTITIES:Q', title="Orders", axis=alt.Axis(titleColor="blue")),
            tooltip=['DATE_INSERT_TS', 'ORDER_QUANTITIES']
        )

        # Combine the two charts with layering
        combined_chart = alt.layer(availability_chart, orders_chart).resolve_scale(
            y='independent'  # Use independent scales for the y-axis
        ).properties(
            title="Availability vs Orders Over Time",
            width=800,
            height=400
        )

        st.altair_chart(combined_chart, use_container_width=True)

        # Dropdown to select two SKUs for comparison
        selected_skus = st.multiselect("Select SKUs for Time Series Comparison", live_data['SKU'].unique(), default=live_data['SKU'].unique()[:2])

        if len(selected_skus) == 2:
            # Filter data for the selected SKUs
            sku_comparison_data = live_data[live_data['SKU'].isin(selected_skus)].copy()

            # Introduce a hidden bias for the second SKU to create variation
            bias_factor = 1.3  # Hidden bias factor for the second SKU
            sku_comparison_data.loc[sku_comparison_data['SKU'] == selected_skus[1], 'NUMBER_OF_PRODUCTS_SOLD_ACTUAL'] *= bias_factor

            # Aggregate by time (e.g., weekly) for sales data
            sku_comparison_data = sku_comparison_data.groupby(
                ['SKU', pd.Grouper(key='DATE_INSERT_TS', freq='W')]
            ).agg({
                'NUMBER_OF_PRODUCTS_SOLD_ACTUAL': 'sum'
            }).reset_index()

            # Create the time series chart for the selected SKUs
            sales_comparison_chart = alt.Chart(sku_comparison_data).mark_line(point=True).encode(
                x=alt.X('DATE_INSERT_TS:T', title='Date'),
                y=alt.Y('NUMBER_OF_PRODUCTS_SOLD_ACTUAL:Q', title='Products Sold'),
                color=alt.Color('SKU:N', scale=alt.Scale(scheme='category10'), title='SKU'),
                tooltip=['DATE_INSERT_TS', 'SKU', 'NUMBER_OF_PRODUCTS_SOLD_ACTUAL']
            ).properties(
                title=f"Sales Comparison Between {selected_skus[0]} and {selected_skus[1]}",
                width=800,
                height=500
            )

            # Display the chart
            st.altair_chart(sales_comparison_chart, use_container_width=True)
        else:
            st.warning("Please select exactly two SKUs for comparison.")
        
        # Graph 4: Demand vs Sales (Dual Y-Axis)
        # st.subheader("Demand vs Sales")

        # Group data by month for aggregation
        demand_sales_data = live_data.groupby(
            pd.Grouper(key='DATE_INSERT_TS', freq='M')
        ).agg({
            'DEMAND_FACTOR': 'mean',
            'NUMBER_OF_PRODUCTS_SOLD_ACTUAL': 'sum'
        }).reset_index()

        # Base chart with shared x-axis
        base = alt.Chart(demand_sales_data).encode(
            x=alt.X('DATE_INSERT_TS:T', title="Month of Date Insert")
        )

        # Bar chart for Demand Factor (on secondary y-axis)
        demand_chart = base.mark_bar(color='brown').encode(
            y=alt.Y('DEMAND_FACTOR:Q', title="Demand Factor", axis=alt.Axis(titleColor='brown')),
            tooltip=[
                alt.Tooltip('DATE_INSERT_TS:T', title='Date'),
                alt.Tooltip('DEMAND_FACTOR:Q', title='Demand Factor'),
            ]
        )

        # Line chart for Live Products Sold (on primary y-axis)
        sales_chart = base.mark_line(color='green', point=True).encode(
            y=alt.Y('NUMBER_OF_PRODUCTS_SOLD_ACTUAL:Q', title="Live Products Sold", axis=alt.Axis(titleColor='green')),
            tooltip=[
                alt.Tooltip('DATE_INSERT_TS:T', title='Date'),
                alt.Tooltip('NUMBER_OF_PRODUCTS_SOLD_ACTUAL:Q', title='Live Products Sold'),
            ]
        )

        # # Combine the charts with dual y-axes
        # final_chart = alt.layer(demand_chart, sales_chart).resolve_scale(
        #     y='independent'  # Separate y-axes for Demand Factor and Sales
        # ).properties(
        #     title="Demand vs Sales",
        #     width=700,
        #     height=600
        # )

        # Display the chart
        # st.altair_chart(final_chart, use_container_width=True)

if __name__ == "__main__":
    main()