# app.py

# Step A: basic imports
import streamlit as st
import pandas as pd
import plotly.express as px

# Step B: set page config (title + layout)
st.set_page_config(
    page_title="Global Superstore Analytics",
    layout="wide"
)

# Step C: load and prepare data
@st.cache_data
def load_data():
    file_path = "output/superstore_clean.csv"   # cleaned file from the notebook
    df = pd.read_csv(file_path, parse_dates=["OrderDate", "ShipDate"])

    # rebuild useful columns (just in case)
    df["OrderYear"] = df["OrderDate"].dt.year
    df["OrderMonth"] = df["OrderDate"].dt.month
    df["OrderYearMonth"] = df["OrderDate"].dt.to_period("M").astype(str)
    df["ProfitMargin"] = df["Profit"] / df["Sales"]

    # shipping days & late flag
    df["ShippingDays"] = (df["ShipDate"] - df["OrderDate"]).dt.days

    def is_late_delivery(row):
        days = row["ShippingDays"]
        mode = row["ShipMode"]

        if pd.isna(days):
            return pd.NA

        if mode == "First Class":
            return days > 2
        elif mode == "Second Class":
            return days > 4
        elif mode == "Standard Class":
            return days > 7
        else:
            return days > 5

    df["IsLate"] = df.apply(is_late_delivery, axis=1)

    return df


# ---------- PAGE FUNCTIONS ----------

def page_executive(data):
    """Executive Overview page."""

    # KPIs
    total_sales = data["Sales"].sum()
    total_profit = data["Profit"].sum()
    overall_margin = total_profit / total_sales
    total_orders = data["OrderID"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales", f"${total_sales:,.0f}")
    col2.metric("Total Profit", f"${total_profit:,.0f}")
    col3.metric("Profit Margin", f"{overall_margin:.1%}")
    col4.metric("Number of Orders", f"{total_orders:,}")

    st.markdown("---")

    # Monthly sales
    monthly = (
        data
        .groupby("OrderYearMonth")
        .agg(MonthlySales=("Sales", "sum"),
             MonthlyProfit=("Profit", "sum"))
        .reset_index()
        .sort_values("OrderYearMonth")
    )

    st.subheader("Sales Over Time (Monthly)")
    fig_line = px.line(
        monthly,
        x="OrderYearMonth",
        y="MonthlySales",
        markers=True,
        labels={"OrderYearMonth": "Order Month", "MonthlySales": "Sales"}
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Sales by Region
    region_summary = (
        data
        .groupby("Region")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
        .reset_index()
    )
    region_summary["ProfitMargin"] = (
        region_summary["Profit"] / region_summary["Sales"]
    )

    st.subheader("Sales by Region")
    fig_region = px.bar(
        region_summary,
        x="Region",
        y="Sales",
        hover_data=["Profit", "ProfitMargin"],
        labels={"Sales": "Total Sales"}
    )
    st.plotly_chart(fig_region, use_container_width=True)


def page_product_category(data):
    """Product & Category Performance page."""

    st.subheader("Category and SubCategory Performance")

    # Summary by Category & SubCategory
    cat_sub = (
        data
        .groupby(["Category", "SubCategory"])
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
        .reset_index()
    )
    cat_sub["ProfitMargin"] = cat_sub["Profit"] / cat_sub["Sales"]

    # Profit by Category
    cat_profit = (
        data
        .groupby("Category")
        .agg(TotalProfit=("Profit", "sum"))
        .reset_index()
        .sort_values("TotalProfit", ascending=False)
    )

    fig_cat = px.bar(
        cat_profit,
        x="Category",
        y="TotalProfit",
        labels={"TotalProfit": "Total Profit"},
        title="Total Profit by Category"
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    # Top 10 SubCategories by Profit
    sub_profit = (
        data
        .groupby("SubCategory")
        .agg(TotalProfit=("Profit", "sum"))
        .reset_index()
        .sort_values("TotalProfit", ascending=False)
    )
    top_sub = sub_profit.head(10)

    fig_sub = px.bar(
        top_sub,
        x="SubCategory",
        y="TotalProfit",
        labels={"TotalProfit": "Total Profit"},
        title="Top 10 SubCategories by Profit"
    )
    fig_sub.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_sub, use_container_width=True)

    st.markdown("---")

    # Category vs Region matrix (heatmap of Profit)
    pivot = (
        data
        .pivot_table(
            index="Category",
            columns="Region",
            values="Profit",
            aggfunc="sum"
        )
    )

    st.subheader("Profit by Category and Region")
    fig_heat = px.imshow(
        pivot,
        labels=dict(x="Region", y="Category", color="Profit"),
        aspect="auto"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("#### Unprofitable Products (Total Profit < 0)")
    product_perf = (
        data
        .groupby(["ProductID", "ProductName", "Category", "SubCategory"])
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
        .reset_index()
    )
    product_perf["ProfitMargin"] = product_perf["Profit"] / product_perf["Sales"]

    unprofitable = (
        product_perf
        .loc[product_perf["Profit"] < 0]
        .sort_values("Profit")
        .head(20)
    )

    st.dataframe(unprofitable)
    # allow user to download the full unprofitable products list
    csv_unprofitable = product_perf.loc[product_perf["Profit"] < 0].sort_values("Profit")
    csv_bytes = csv_unprofitable.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download all unprofitable products as CSV",
        data=csv_bytes,
        file_name="unprofitable_products_full.csv",
        mime="text/csv"
    )



def page_customer_shipping(data):
    """Customer & Shipping Insights page."""

    # Customer summary
    customer_perf = (
        data
        .groupby(["CustomerID", "CustomerName", "Segment"])
        .agg(
            TotalSales=("Sales", "sum"),
            TotalProfit=("Profit", "sum"),
            NumOrders=("OrderID", "nunique"),
            LastOrderDate=("OrderDate", "max")
        )
        .reset_index()
    )
    customer_perf["ProfitMargin"] = (
        customer_perf["TotalProfit"] / customer_perf["TotalSales"]
    )

    st.subheader("Top 10 Customers by Sales")
    top_customers = (
        customer_perf
        .sort_values("TotalSales", ascending=False)
        .head(10)
    )
    fig_cust = px.bar(
        top_customers,
        x="TotalSales",
        y="CustomerName",
        orientation="h",
        labels={"TotalSales": "Total Sales", "CustomerName": "Customer"},
    )
    fig_cust.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_cust, use_container_width=True)

    st.markdown("---")

    # Segment summary
    segment_summary = (
        data
        .groupby("Segment")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("OrderID", "nunique"),
            Customers=("CustomerID", "nunique")
        )
        .reset_index()
    )
    segment_summary["ProfitMargin"] = (
        segment_summary["Profit"] / segment_summary["Sales"]
    )

    st.subheader("Performance by Customer Segment")
    fig_seg = px.bar(
        segment_summary,
        x="Segment",
        y="Sales",
        hover_data=["Profit", "ProfitMargin", "Orders", "Customers"],
        labels={"Sales": "Total Sales"}
    )
    st.plotly_chart(fig_seg, use_container_width=True)

    st.markdown("---")

    # Shipping KPIs
    avg_shipping_days = data["ShippingDays"].mean()
    late_mask = data["IsLate"].dropna()
    late_rate = late_mask.mean()

    col1, col2 = st.columns(2)
    col1.metric("Average Shipping Time (days)", f"{avg_shipping_days:.2f}")
    col2.metric("Late Delivery Rate", f"{late_rate:.1%}")

    # Shipping by ShipMode
    shipmode_summary = (
        data
        .groupby("ShipMode")
        .agg(
            AvgShippingDays=("ShippingDays", "mean"),
            Orders=("OrderID", "nunique")
        )
        .reset_index()
    )
    late_by_mode = (
        data
        .dropna(subset=["IsLate"])
        .groupby("ShipMode")["IsLate"]
        .mean()
        .reset_index()
        .rename(columns={"IsLate": "LateRate"})
    )
    shipmode_summary = shipmode_summary.merge(late_by_mode, on="ShipMode", how="left")

    st.subheader("Average Shipping Time by Ship Mode")
    fig_ship_days = px.bar(
        shipmode_summary,
        x="ShipMode",
        y="AvgShippingDays",
        labels={"AvgShippingDays": "Average Shipping Days"}
    )
    st.plotly_chart(fig_ship_days, use_container_width=True)

    st.subheader("Late Delivery Rate by Ship Mode")
    fig_ship_late = px.bar(
        shipmode_summary,
        x="ShipMode",
        y="LateRate",
        labels={"LateRate": "Late Rate"}
    )
    st.plotly_chart(fig_ship_late, use_container_width=True)


# ---------- MAIN APP ----------

def main():
    st.title("Global Superstore – Sales & Profitability Dashboard")
    st.caption("Built with Python (Streamlit) using Global Superstore data")

    data = load_data()

    # Sidebar filters
    st.sidebar.header("Filters")

    year_options = sorted(data["OrderYear"].unique())
    selected_years = st.sidebar.multiselect(
        "Year",
        options=year_options,
        default=year_options
    )

    region_options = sorted(data["Region"].dropna().unique())
    selected_regions = st.sidebar.multiselect(
        "Region",
        options=region_options,
        default=region_options
    )

    segment_options = sorted(data["Segment"].dropna().unique())
    selected_segments = st.sidebar.multiselect(
        "Segment",
        options=segment_options,
        default=segment_options
    )

    # apply filters
    filtered = data[
        data["OrderYear"].isin(selected_years)
        & data["Region"].isin(selected_regions)
        & data["Segment"].isin(selected_segments)
    ]

    st.sidebar.write(f"Rows after filters: {len(filtered):,}")

    # Tabs for pages
    tab1, tab2, tab3 = st.tabs([
        "Executive Overview",
        "Product & Category",
        "Customer & Shipping"
    ])

    with tab1:
        page_executive(filtered)

    with tab2:
        page_product_category(filtered)

    with tab3:
        page_customer_shipping(filtered)


if __name__ == "__main__":
    main()
