import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import time, datetime
plt.style.use("default")

def createDailyrent_df(strdate, enddate, df):
    if((strdate) == enddate):
        rule_char = 'h'
    else:
        rule_char = 'D'
    
    daily_rent_df = df.resample(rule=rule_char, on="dteday").agg({
        "instant" : "nunique",
        "season" : "max",
        "weathersit" : "max",
        "casual" : "sum",
        "registered" : "sum",
        "cnt" : "sum"
    })
    daily_rent_df = daily_rent_df.reset_index()
    daily_rent_df.rename(columns={
        "instant" : "rent_count",
        "cnt" : "total"
    }, inplace=True)

    return daily_rent_df

def createBySeason_df(df):
    basedon_season_df = df.groupby(by="season", as_index=False).agg({
        "casual" : "sum",
        "registered" : "sum",
        "total" : "sum"
    })
    return basedon_season_df

def createByWeathersit_df(df):
    basedon_weather_df = df.groupby(by="weathersit", as_index=False).agg({
        "casual" : "sum",
        "registered" : "sum",
        "cnt" : "sum"
    })
    basedon_weather_df.reset_index(inplace=True)
    basedon_weather_df = basedon_weather_df.rename(columns={
        "cnt" : "total"
    })
    return basedon_weather_df

def createTotalUsers_df(df):
    cas_cust_rent_freq = df["casual"].sum()
    reg_cust_rent_freq = df["registered"].sum()
    cust_freq_df = pd.DataFrame({
        "customer_type" : ["Casual", "Registered"],
        "frequency" : [cas_cust_rent_freq, reg_cust_rent_freq]
    })
    return cust_freq_df

#Mengekspor data hour.csv
hour_df = pd.read_csv("hour.csv", delimiter=';')

hour_df.sort_values(by="instant", inplace=True)
hour_df.reset_index(inplace=True)
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])

#Mengidentifikasi batas tanggal dan batas jam
min_date = hour_df["dteday"].min()
max_date = hour_df["dteday"].max()
min_hour = 0
max_hour = 23

with st.sidebar:
    st.image("https://raw.githubusercontent.com/slmnf29/photo/refs/heads/main/black-electric-bike-18922.png", width=256)
    start_date, end_date = st.date_input(
        label="Rentang Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

#Menggabungkan data tanggal dan data jam
start_time = datetime.combine(start_date, time(hour=0))
end_time = datetime.combine(end_date, time(hour=23))
hour_df = hour_df[(hour_df["dteday"] >= str(start_time)) & (hour_df["dteday"] <= str(end_time))]

#Mengidentifikasi satu-per-satu var yang dibutuhkan
daily_rent_df = createDailyrent_df(start_date, end_date, hour_df)
total_users_df = createTotalUsers_df(daily_rent_df)
by_season_df = createBySeason_df(daily_rent_df)
by_weathersit_df = createByWeathersit_df(hour_df)


#Ketika yang dilihat hanya 1 hari, maka semuanya akan menampilkan penyewaan per-jam
#Menampilkan grafik penyewaan harian
st.subheader("Penyewaan Harian")
col1, col2, col3 = st.columns(3)
with col1:
    total_rent = daily_rent_df["total"].sum()
    st.metric("Total penyewaan ", value=total_rent)

with col2:
    cas_total_rent = daily_rent_df["casual"].sum()
    st.metric("Total Pengguna Casual Menyewa", value=cas_total_rent)

with col3:
    reg_total_rent = daily_rent_df["registered"].sum()
    st.metric("Total Pengguna Registered Menyewa", value=reg_total_rent)

fig, ax = plt.subplots(figsize=(15, 7))
ax.plot(daily_rent_df["dteday"], daily_rent_df["casual"], label="Casual", color="#2cde53")
ax.plot(daily_rent_df["dteday"], daily_rent_df["registered"], label="Registered", color="#4287f5")

ax.tick_params(axis='x', labelsize=15, rotation=45)
ax.tick_params(axis='y', labelsize=15)
ax.grid()
ax.legend()
st.pyplot(fig)


#Menampilkan perbandingan pengguna casual dengan pengguna registered
st.subheader("Perbandingan Pengguna Casual Dengan Pengguna Registered")
col1, col2 = st.columns(2)
with col1:
    colors = ["#2cde53", "#4287f5"]
    explode = [0, 0.1]
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.pie(
        x=total_users_df["frequency"],
        labels=total_users_df["customer_type"],
        autopct='%0.2f%%',
        textprops={"fontsize":25},
        colors=colors,
        explode=explode,
        radius=0.8
    )
    st.pyplot(fig)
with col2:
    total_rent = daily_rent_df["total"].sum()
    st.metric("Total penyewaan ", value=total_rent)

    cas_total_rent = daily_rent_df["casual"].sum()
    st.metric("Total Pengguna Casual Menyewa", value=cas_total_rent)

    reg_total_rent = daily_rent_df["registered"].sum()
    st.metric("Total Pengguna Registered Menyewa", value=reg_total_rent)



#Menampilkan jumlah penyewaan berdasarkan cuaca
st.subheader("Jumlah Penyewaan Berdasarkan Cuaca")
palette = ["#2cde53", "#bfbfbf", "#bfbfbf", "#bfbfbf"]
fig, ax = plt.subplots(figsize=(15, 8))
sns.barplot(orient='h', x="casual", y="weathersit", data=by_weathersit_df.sort_values(by="casual", ascending=False), hue="weathersit", palette=palette, height=0.7, width=0.05, align="center")
ax.set_title("Pengguna Casual", size=30)
ax.set_xlabel("")
ax.set_ylabel("")
ax.tick_params(axis='x', labelsize=30, rotation=25)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)

palette = ["#4287f5", "#bfbfbf", "#bfbfbf", "#bfbfbf"]
sns.barplot(orient='h', x="registered", y="weathersit", data=by_weathersit_df.sort_values(by="registered", ascending=False), hue="weathersit", palette=palette, height=0.7, width=0.05, align="center")
ax.set_title("Pengguna Registered", size=30)
ax.set_xlabel("")
ax.set_ylabel("")
ax.tick_params(axis='x', labelsize=30, rotation=25)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)



#menampilkan penyewaan berdasarkan musim
st.subheader("Jumlah Penyewaan Berdasarkan Musim")
col1, col2 = st.columns(2)
with col1:
    palette = ["#2cde53", "#bfbfbf", "#bfbfbf", "#bfbfbf"]
    fig, ax = plt.subplots(figsize=(5, 6))
    sns.barplot(x="season", y="casual", data=by_season_df.sort_values(by="casual", ascending=False), hue="season", palette=palette)
    ax.set_title("Pengguna Casual", size=12)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

with col2:
    palette = ["#4287f5", "#bfbfbf", "#bfbfbf", "#bfbfbf"]
    fig, ax = plt.subplots(figsize=(5, 6))
    sns.barplot(x="season", y="registered", data=by_season_df.sort_values(by="registered", ascending=False), hue="season", palette=palette)
    ax.set_title("Pengguna Registered", size=12)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

st.caption("Copyright (c) Salman Alfarizi 2025")