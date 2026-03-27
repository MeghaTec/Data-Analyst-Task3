
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Set UTF-8 encoding for Windows compatibility
import sys
import io
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

# Page Configuration
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        padding: 1rem 0;
    }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1.5rem;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('sales_data.csv')
    # Data Cleaning
    df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
    df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce').fillna(0)
    df['Return'] = pd.to_numeric(df['Return'], errors='coerce').fillna(0)
    df['SatisfactionScore'] = pd.to_numeric(df['SatisfactionScore'], errors='coerce')
    df['Region'] = df['Region'].fillna('Unknown')
    return df

df = load_data()

# Header
st.markdown('<p class="main-header">Sales Analytics Dashboard</p>', 
            unsafe_allow_html=True)
st.markdown("---")

# Sidebar Filters
st.sidebar.header("Filters")

# Region Filter
regions = ['All'] + list(df['Region'].unique())
selected_region = st.sidebar.selectbox("Select Region", regions)

# Customer Type Filter
customer_types = ['All'] + list(df['CustomerType'].unique())
selected_customer = st.sidebar.selectbox("Customer Type", customer_types)

# Sales Channel Filter
channels = ['All'] + list(df['SalesChannel'].unique())
selected_channel = st.sidebar.selectbox("Sales Channel", channels)

# Product Category Filter
categories = ['All'] + list(df['ProductCategory'].unique())
selected_category = st.sidebar.selectbox("Product Category", categories)

# Apply Filters
filtered_df = df.copy()
if selected_region != 'All':
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]
if selected_customer != 'All':
    filtered_df = filtered_df[filtered_df['CustomerType'] == selected_customer]
if selected_channel != 'All':
    filtered_df = filtered_df[filtered_df['SalesChannel'] == selected_channel]
if selected_category != 'All':
    filtered_df = filtered_df[filtered_df['ProductCategory'] == selected_category]

# Calculate KPIs
total_revenue = filtered_df['Sales'].sum()
total_transactions = len(filtered_df)
aov = filtered_df['Sales'].mean()
return_rate = (filtered_df['Return'].sum() / total_transactions) * 100 if total_transactions > 0 else 0
avg_satisfaction = filtered_df['SatisfactionScore'].mean()
vip_sales = filtered_df[filtered_df['CustomerType']=='VIP']['Sales'].sum()
vip_share = (vip_sales / total_revenue * 100) if total_revenue > 0 else 0

# KPI Cards
st.subheader("Core KPIs")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="metric-value">${total_revenue:,.0f}</div>
        <div class="metric-label">Total Revenue</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="metric-value">${aov:,.0f}</div>
        <div class="metric-label">Avg Order Value</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="metric-value">{return_rate:.1f}%</div>
        <div class="metric-label">Return Rate</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="metric-value">{avg_satisfaction:.1f}</div>
        <div class="metric-label">Avg Satisfaction</div>
    </div>
    """, unsafe_allow_html=True)

with kpi5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="metric-value">{vip_share:.1f}%</div>
        <div class="metric-label">VIP Revenue Share</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Main Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by Customer Segment")
    seg_rev = filtered_df.groupby('CustomerType')['Sales'].sum().reset_index()
    fig1 = px.bar(seg_rev, x='CustomerType', y='Sales', 
                  color='CustomerType',
                  color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    fig1.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Revenue by Region")
    reg_rev = filtered_df.groupby('Region')['Sales'].sum().reset_index()
    fig2 = px.pie(reg_rev, values='Sales', names='Region',
                  color_discrete_sequence=px.colors.qualitative.Set3)
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

# Second Row Charts
col3, col4 = st.columns(2)

with col3:
    st.subheader("Sales Channel Performance")
    chan_perf = filtered_df.groupby('SalesChannel').agg({
        'Sales': 'sum',
        'SatisfactionScore': 'mean'
    }).reset_index()
    fig3 = px.bar(chan_perf, x='SalesChannel', y='Sales',
                  color='SatisfactionScore',
                  color_continuous_scale='RdYlGn')
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Top Product Categories")
    cat_rev = filtered_df.groupby('ProductCategory')['Sales'].sum().nlargest(5).reset_index()
    fig4 = px.bar(cat_rev, x='Sales', y='ProductCategory', orientation='h',
                  color='Sales', color_continuous_scale='Blues')
    fig4.update_layout(height=400)
    st.plotly_chart(fig4, use_container_width=True)

# Deep Dive Section
st.markdown("---")
st.subheader("Deep-Dive Analysis: Customer Segmentation")

# Segmentation Table
st.write("### Segment Performance Metrics")
seg_metrics = filtered_df.groupby('CustomerType').agg({
    'Sales': ['sum', 'mean'],
    'Return': 'sum',
    'SatisfactionScore': 'mean',
    'CustomerID': 'count'
}).round(2)
seg_metrics.columns = ['Total_Sales', 'Avg_Order_Value', 'Total_Returns', 
                       'Avg_Satisfaction', 'Transactions']
seg_metrics['Return_Rate'] = (seg_metrics['Total_Returns'] / 
                              seg_metrics['Transactions']) * 100
st.dataframe(seg_metrics.style.format({
    'Total_Sales': '${:,.2f}',
    'Avg_Order_Value': '${:,.2f}',
    'Return_Rate': '{:.2f}%'
}))

# Satisfaction Distribution
st.write("### Satisfaction Score Distribution")
fig5 = px.histogram(filtered_df, x='SatisfactionScore', nbins=10,
                    color='CustomerType', barmode='overlay',
                    opacity=0.7)
fig5.update_layout(height=400)
st.plotly_chart(fig5, use_container_width=True)

# Data Export
st.markdown("---")
st.subheader("Export Data")
if st.button("Download Filtered Data"):
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='filtered_sales_data.csv',
        mime='text/csv'
    )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>Sales Analytics Dashboard | Built with Streamlit & Plotly</p>
</div>
""", unsafe_allow_html=True)
