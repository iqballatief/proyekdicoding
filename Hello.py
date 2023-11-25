import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# IMPORT DATA
data_2018 = pd.read_csv("2018.csv")

# HELPER FUNCTION
# daily orders
def create_daily_orders_df(data_2018):
    daily_orders_df = data_2018.resample(rule='D', on='order_purchase_timestamp').agg({
        "product_id":"nunique",
        "total_revenue":"sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "product_id":"order_count",
        "total_revenue": "revenue"
    }, inplace=True)

    return daily_orders_df

# sum_order_items
def create_sum_order_items_df(data_2018):
    sum_order_items_df = data_2018.groupby("product_category_name").total_frequency.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

# rfm
def create_rfm_df(data_2018):
    rfm_df = data_2018.groupby(by="product_id", as_index=False).agg({
        "order_purchase_timestamp": "max", 
        "customer_id": "nunique",
        "total_revenue": "sum"
    })
    rfm_df.columns = ["product_id", "max_order_timestamp", "total_frequency", "total_revenue"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = data_2018["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df





# CHANGE DATA TYPE
datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
data_2018.sort_values(by="order_purchase_timestamp", inplace=True)
data_2018.reset_index(inplace=True)
 
for column in datetime_columns:
    data_2018[column] = pd.to_datetime(data_2018[column])



# CREATE FILTER
min_date = data_2018["order_purchase_timestamp"].min()
max_date = data_2018["order_purchase_timestamp"].max()
 
with st.sidebar:
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = data_2018[(data_2018["order_purchase_timestamp"] >= str(start_date)) & 
                (data_2018["order_purchase_timestamp"] <= str(end_date))]


# Creating df
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
rfm_df = create_rfm_df(main_df)


# DASHBOARD TITLE
st.header('E-Commerce Public Dashboard 2018 :sparkles:')

st.subheader('Daily Orders')
 


# DAILY ORDERS

# order_date_df
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "USD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)


# sum_order_date_df
st.subheader("Best & Worst Performing Product")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="total_frequency", y="product_category_name", data=sum_order_items_df.head(3), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="total_frequency", y="product_category_name", data=sum_order_items_df.sort_values(by="total_frequency", ascending=True).head(3), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)


# rfm_df
st.subheader("Best Products Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.total_frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.total_revenue.mean(), "USD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="product_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("product_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="total_frequency", x="product_id", data=rfm_df.sort_values(by="total_frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("product_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="total_revenue", x="product_id", data=rfm_df.sort_values(by="total_revenue", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("product_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)

 
