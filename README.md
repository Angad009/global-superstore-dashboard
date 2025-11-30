# Global Superstore – Sales & Profitability Dashboard (Python + Streamlit)

Retail analytics dashboard built in **Python** using the popular **Global Superstore / Superstore** dataset from Kaggle.  
The goal is to replicate a business-style BI dashboard (like Power BI) but fully in code, showing both technical and business skills.

---

## 🎯 Project Objectives

- Analyse **sales** and **profitability** across categories, regions, and customer segments.
- Build an **interactive dashboard** with multiple views in **Streamlit**.
- Engineer useful business KPIs:
  - Profit Margin  
  - Shipping Time (days)  
  - Late-Delivery Rate  
- Provide exportable tables such as a list of **unprofitable products**.

---

## 🧱 Tech Stack

- **Language:** Python  
- **Libraries:** `pandas`, `plotly.express`, `streamlit`  
- **Notebook:** Jupyter (for data prep and exploration)

---

## 📂 Project Structure

global_superstore_dashboard/  
├─ app.py  — Streamlit dashboard application  
├─ notebooks/  
│  └─ 01_data_loading_and_cleaning.ipynb  — data prep, feature engineering, EDA  
├─ data/  — raw data (ignored in GitHub)  
│  └─ superstore.csv  — Kaggle Superstore dataset (not included)  
├─ output/  — processed data (ignored in GitHub)  
│  └─ superstore_clean.csv  — cleaned dataset used by the app  
└─ README.md  

> **Note:** `data/` and `output/` are not uploaded to GitHub for size and licensing reasons.

---

## 🗂 Dataset

The dashboard uses the **Superstore / Global Superstore** dataset from Kaggle.  
It contains ~50k order lines with information about:

- Orders (dates, IDs, shipping mode)  
- Products (category, sub-category, product name)  
- Customers (ID, name, segment)  
- Geography (country, region, state, city)  
- Metrics (sales, profit, discount, shipping cost)

To run the project you will need to download the dataset yourself (instructions below).

---

## 📊 Dashboard Pages

### 1. Executive Overview

High-level KPIs and trends for management:

- **KPI Cards:** Total Sales, Total Profit, Profit Margin, Number of Orders.  
- **Time Series:** Monthly sales trend.  
- **Geography:** Sales and profit by Region, with profit margin.

### 2. Product & Category Performance

Helps identify strong and weak areas in the product portfolio:

- Total profit by **Category** (bar chart).  
- Top 10 **Sub-Categories** by profit.  
- **Category vs Region** profit heatmap (matrix-style view).  
- Table of **unprofitable products** (total profit < 0) with:
  - Product ID & Name  
  - Category / Sub-Category  
  - Sales, Profit, Profit Margin  
- Button to **download** the full unprofitable products list as CSV.

### 3. Customer & Shipping Insights

Focus on customer value and delivery performance:

- **Top 10 customers** by total sales (horizontal bar chart).  
- Segment-level summary (Consumer, Corporate, Home Office) with:
  - Sales, Profit, Orders, Number of Customers, Profit Margin.  
- **Shipping KPIs:**
  - Average shipping time (days) based on `OrderDate` and `ShipDate`.  
  - Overall late-delivery rate (custom rules per Ship Mode).  
- Shipping performance by **Ship Mode**:
  - Average shipping days by mode.  
  - Late-delivery rate by mode.

---

## ⚙️ Engineered Features / Business Logic

Some of the features created in the notebook and used by the app:

- `OrderYear`, `OrderMonth`, `OrderYearMonth` – for time-based analysis.  
- `ProfitMargin = Profit / Sales`.  
- `ShippingDays = (ShipDate - OrderDate).days`.  
- `IsLate` flag based on business rules per `ShipMode`, e.g.:
  - First Class late if `ShippingDays > 2`  
  - Second Class late if `ShippingDays > 4`  
  - Standard Class late if `ShippingDays > 7`  

These decisions can be discussed and adjusted depending on business requirements.

---

## 🚀 How to Run Locally

1. **Clone or download this repository**

   - Clone:
     - `git clone https://github.com/YOUR_USERNAME/global-superstore-dashboard.git`  
     - `cd global-superstore-dashboard`  
   - Or download as ZIP and extract.

2. **Download the dataset from Kaggle**

   - Go to Kaggle and search for **“Superstore”** or **“Global Superstore”**.  
   - Download the CSV file.  
   - Save it as: `data/superstore.csv`

3. **(Optional) Regenerate the cleaned dataset**

   - Open the notebook: `notebooks/01_data_loading_and_cleaning.ipynb`.  
   - Run all cells to create `output/superstore_clean.csv`.  

   If you prefer, you can also create your own cleaned CSV and update the path in `app.py`.

4. **Install dependencies**

   Make sure you have Python 3.9+ and pip installed, then run:

   - `pip install streamlit pandas plotly`

5. **Run the Streamlit app**

   - `streamlit run app.py`  

   Streamlit will open a browser window, usually at: `http://localhost:8501/`

---

