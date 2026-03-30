import streamlit as st
import yfinance as yf
import plotly.express as px

st.title("Commodity Intelligence Dashboard 2026")

# Dropdown for the user
target = st.selectbox("Select Commodity", ["GC=F", "CL=F", "HG=F"])

# Fetch and Plot
data = yf.download(target, period="1y").reset_index()
fig = px.area(data, x='Date', y='Close', title=f"Trend for {target}")
st.plotly_chart(fig)