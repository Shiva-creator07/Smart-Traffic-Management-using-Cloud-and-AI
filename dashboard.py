import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient
from datetime import datetime

st.set_page_config(page_title="Traffic Management System", layout="wide", page_icon="🚦")

# Configuration - UPDATE THIS WITH YOUR CONNECTION STRING
MONGO_URI = "mongodb+srv://aryan:aryan3323@cluster0.lpxyvko.mongodb.net/"

@st.cache_resource
def init_database():
    """Initialize MongoDB connection with SSL fix"""
    try:
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=10000
        )
        # Test connection
        client.admin.command('ping')
        return client
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def get_data(client, limit=100):
    """Get data from MongoDB"""
    try:
        db = client['traffic_management']
        collection = db['traffic_data']
        cursor = collection.find().sort('timestamp', -1).limit(limit)
        data = list(cursor)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

# Initialize
client = init_database()

if client is None:
    st.error("❌ Cannot connect to database. Please check your MongoDB URI in the code.")
    st.stop()

# Title
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🚦 Intelligent Traffic Management System")
with col2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    data_limit = st.slider("Data Points", 10, 500, 100)
    auto_refresh = st.checkbox("Auto-refresh (5s)")
    
    st.markdown("---")
    st.header("📊 System Status")
    
    try:
        db = client['traffic_management']
        collection = db['traffic_data']
        total_docs = collection.count_documents({})
        st.metric("Total Records", total_docs)
        
        if total_docs == 0:
            st.warning("⚠️ No data yet")
            if st.button("Insert Test Data"):
                test_doc = {
                    'timestamp': datetime.now(),
                    'camera_id': 'test_cam',
                    'location': 'Test Location',
                    'vehicle_count': 10,
                    'vehicle_types': {'car': 7, 'truck': 2, 'motorcycle': 1},
                    'traffic_density': 'medium',
                    'congestion_level': 45.5,
                    'average_count': 8.5,
                    'trend': 'stable'
                }
                collection.insert_one(test_doc)
                st.success("✓ Test data inserted!")
                time.sleep(1)
                st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

# Auto-refresh logic
if auto_refresh:
    time.sleep(5)
    st.rerun()

# Fetch data
data = get_data(client, limit=data_limit)

if not data:
    st.warning("⚠️ No data available")
    st.info("""
    **Getting Started:**
    1. Make sure `main_fixed.py` is running
    2. Verify your camera is connected
    3. Check MongoDB connection string
    4. Use sidebar to insert test data
    """)
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(data)

# Convert timestamp
if 'timestamp' in df.columns:
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])

# Latest data
latest = df.iloc[0]
previous = df.iloc[1] if len(df) > 1 else latest

# =====================================================
# METRICS ROW
# =====================================================
st.subheader("📊 Real-Time Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    delta = latest['vehicle_count'] - previous['vehicle_count']
    st.metric("Current Vehicles", latest['vehicle_count'], delta=int(delta))

with col2:
    st.metric("Traffic Density", latest['traffic_density'].upper())

with col3:
    delta_cong = latest['congestion_level'] - previous['congestion_level']
    st.metric("Congestion", f"{latest['congestion_level']:.1f}%", 
              delta=f"{delta_cong:.1f}%")

with col4:
    st.metric("Trend", latest['trend'].upper())

st.markdown("---")

# =====================================================
# CHARTS ROW 1
# =====================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Vehicle Count Over Time")
    fig1 = px.line(df, x='timestamp', y='vehicle_count')
    fig1.update_traces(line_color='#1f77b4', line_width=2)
    fig1.update_layout(xaxis_title="Time", yaxis_title="Vehicles", height=350)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🎯 Congestion Level")
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=latest['congestion_level'],
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 60], 'color': "yellow"},
                {'range': [60, 100], 'color': "red"}
            ]
        }
    ))
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# CHARTS ROW 2
# =====================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚗 Traffic Density Distribution")
    density_counts = df['traffic_density'].value_counts()
    fig3 = px.pie(values=density_counts.values, names=density_counts.index)
    fig3.update_layout(height=350)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("📊 Average Vehicle Count")
    fig4 = px.area(df, x='timestamp', y='average_count')
    fig4.update_traces(fillcolor='rgba(31, 119, 180, 0.3)')
    fig4.update_layout(xaxis_title="Time", yaxis_title="Avg Count", height=350)
    st.plotly_chart(fig4, use_container_width=True)

# =====================================================
# VEHICLE TYPES
# =====================================================
st.markdown("---")
st.subheader("🚙 Vehicle Types Analysis")

all_vehicle_types = {}
for _, row in df.iterrows():
    if 'vehicle_types' in row and isinstance(row['vehicle_types'], dict):
        for vtype, count in row['vehicle_types'].items():
            all_vehicle_types[vtype] = all_vehicle_types.get(vtype, 0) + count

if all_vehicle_types:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        vtype_df = pd.DataFrame(list(all_vehicle_types.items()), 
                               columns=['Type', 'Count'])
        fig5 = px.bar(vtype_df, x='Type', y='Count', color='Count')
        fig5.update_layout(height=300)
        st.plotly_chart(fig5, use_container_width=True)
    
    with col2:
        st.markdown("#### Breakdown")
        total = sum(all_vehicle_types.values())
        for vtype, count in sorted(all_vehicle_types.items(), 
                                  key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            st.metric(vtype.capitalize(), f"{count} ({percentage:.1f}%)")
else:
    st.info("No vehicle type data available")

# =====================================================
# TREND ANALYSIS
# =====================================================
st.markdown("---")
st.subheader("📈 Trend Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("##### Traffic Trends")
    trend_counts = df['trend'].value_counts()
    for trend, count in trend_counts.items():
        emoji = "📈" if trend == "increasing" else "📉" if trend == "decreasing" else "➡️"
        st.markdown(f"{emoji} **{trend.capitalize()}**: {count}x")

with col2:
    st.markdown("##### Peak Traffic")
    peak_idx = df['vehicle_count'].idxmax()
    peak_time = df.loc[peak_idx, 'timestamp']
    peak_count = df.loc[peak_idx, 'vehicle_count']
    st.info(f"🕐 {peak_time.strftime('%H:%M:%S')}\n\n🚗 {peak_count} vehicles")

with col3:
    st.markdown("##### Low Traffic")
    low_idx = df['vehicle_count'].idxmin()
    low_time = df.loc[low_idx, 'timestamp']
    low_count = df.loc[low_idx, 'vehicle_count']
    st.success(f"🕐 {low_time.strftime('%H:%M:%S')}\n\n🚗 {low_count} vehicles")

# =====================================================
# DATA TABLE
# =====================================================
st.markdown("---")
st.subheader("📋 Recent Traffic Data")

display_df = df[['timestamp', 'vehicle_count', 'traffic_density', 
               'congestion_level', 'trend']].head(20).copy()
display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
display_df['congestion_level'] = display_df['congestion_level'].round(1)
display_df.columns = ['Time', 'Vehicles', 'Density', 'Congestion %', 'Trend']

st.dataframe(display_df, use_container_width=True, height=300)

# =====================================================
# STATISTICS
# =====================================================
st.markdown("---")
st.subheader("📊 Statistical Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Average", f"{df['vehicle_count'].mean():.1f}")
with col2:
    st.metric("Maximum", int(df['vehicle_count'].max()))
with col3:
    st.metric("Minimum", int(df['vehicle_count'].min()))
with col4:
    st.metric("Std Dev", f"{df['vehicle_count'].std():.1f}")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data points: {len(df)}")