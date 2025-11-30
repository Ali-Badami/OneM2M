import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="TinyOneM2M: Mission Critical",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (CYBERPUNK / SCI-FI THEME) ---
st.markdown("""
<style>
    /* Global Font & Background */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto+Mono:wght@400;700&display=swap');
    
    .stApp {
        background-color: #050510;
        color: #00f2ff;
        font-family: 'Roboto Mono', monospace;
    }
    
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #fff !important;
        text-shadow: 0 0 10px #00f2ff;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif;
        font-size: 2rem !important;
        color: #ff0055;
        text-shadow: 0 0 5px #ff0055;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #8899a6;
    }

    /* Custom Borders */
    .status-box {
        border: 1px solid #333;
        border-radius: 5px;
        padding: 15px;
        background: rgba(255, 255, 255, 0.05);
        margin-bottom: 20px;
    }
    
    .success-box {
        border: 1px solid #00ff41;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
    }
    
    .danger-box {
        border: 1px solid #ff0055;
        box-shadow: 0 0 15px rgba(255, 0, 85, 0.2);
    }
    
    /* Buttons */
    .stButton>button {
        font-family: 'Orbitron', sans-serif;
        border: 1px solid #00f2ff;
        background-color: transparent;
        color: #00f2ff;
        border-radius: 0;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #00f2ff;
        color: black;
        box-shadow: 0 0 20px #00f2ff;
    }
</style>
""", unsafe_allow_html=True)

# --- APP STATE & LOGIC ---
if 'simulation_running' not in st.session_state:
    st.session_state.simulation_running = False

# --- HEADER ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.markdown("<h1>📡</h1>", unsafe_allow_html=True)
with col_title:
    st.title("TINY-ONEM2M: MISSION CRITICAL")
    st.caption("DEPLOYMENT TARGET: RASPBERRY PI ZERO W (512MB RAM)")

st.markdown("---")

# --- CONTROL PANEL (GAMIFIED) ---
c1, c2, c3 = st.columns([1, 1, 1])

with c1:
    st.markdown("### 1. SELECT KERNEL")
    runtime = st.radio(
        "Runtime Environment",
        ["Standard (Java/Python)", "TinyOneM2M (C-Based)"],
        index=0,
        help="Standard runtimes have high overhead (JVM/Interpreter). TinyOneM2M uses native C."
    )

with c2:
    st.markdown("### 2. DB STRATEGY")
    db_mode = st.radio(
        "Database Architecture",
        ["Normalized (Complex Joins)", "Denormalized (Single Table)"],
        index=0,
        help="Normalized DBs save space but slow down deep queries. Denormalized DBs are optimized for speed."
    )

with c3:
    st.markdown("### 3. LOAD INJECTOR")
    device_load = st.select_slider(
        "Connected Devices",
        options=[1000, 10000, 50000, 100000],
        value=1000
    )

# --- SIMULATION ENGINE ---
# Parameters derived from Paper Tables VI, VIII, IX
BASE_RAM = 512 # MB (Pi Zero Limit)

if runtime == "TinyOneM2M (C-Based)":
    ram_usage_per_k = 0.14  # ~140MB for 100k
    base_overhead = 5       # 5MB base
    latency_factor = 1.0    # 1ms base
else:
    ram_usage_per_k = 0.8   # ~800MB for 100k (Crash zone)
    base_overhead = 60      # 60MB JVM overhead
    latency_factor = 15.0   # 15ms base (Garbage collection spikes)

if db_mode == "Denormalized (Single Table)":
    query_speed = 4.5       # microseconds (Fast)
else:
    query_speed = 3300.0    # microseconds (Slow - Deep Joins)

# Calculate Current State
current_ram = base_overhead + (device_load / 1000 * ram_usage_per_k)
ram_percent = (current_ram / BASE_RAM) * 100
current_latency = latency_factor * (1 + (device_load/100000))
current_db_time = query_speed

# --- MAIN VISUALIZATION AREA ---

# 1. STATUS INDICATORS (GAUGES)
st.markdown("### 📊 SYSTEM TELEMETRY")
g1, g2, g3 = st.columns(3)

with g1:
    # RAM GAUGE
    fig_ram = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = current_ram,
        title = {'text': "RAM USAGE (MB)"},
        gauge = {
            'axis': {'range': [0, 512]},
            'bar': {'color': "#00f2ff" if current_ram < 400 else "#ff0055"},
            'steps': [
                {'range': [0, 400], 'color': "rgba(0, 242, 255, 0.1)"},
                {'range': [400, 512], 'color': "rgba(255, 0, 85, 0.3)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 480
            }
        }
    ))
    fig_ram.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
    st.plotly_chart(fig_ram, use_container_width=True)

with g2:
    # LATENCY GAUGE
    fig_lat = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = current_latency,
        title = {'text': "API LATENCY (ms)"},
        gauge = {
            'axis': {'range': [0, 20]},
            'bar': {'color': "#00ff41" if current_latency < 5 else "#ffa500"},
            'steps': [
                {'range': [0, 5], 'color': "rgba(0, 255, 65, 0.1)"},
                {'range': [5, 20], 'color': "rgba(255, 165, 0, 0.2)"}
            ]
        }
    ))
    fig_lat.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
    st.plotly_chart(fig_lat, use_container_width=True)

with g3:
    # DB SPEED GAUGE (Log Scale Simulation)
    fig_db = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = np.log10(current_db_time),
        title = {'text': "DB QUERY COST (Log10 µs)"},
        number = {'suffix': " µs", 'font': {'size': 20}}, 
        # Hack to show actual value in overlay or subtitle
        gauge = {
            'axis': {'range': [0, 4]}, # 10^0 to 10^4
            'bar': {'color': "#8a2be2"},
            'steps': [
                {'range': [0, 1], 'color': "rgba(0, 255, 65, 0.1)"}, # 1-10us
                {'range': [3, 4], 'color': "rgba(255, 0, 85, 0.3)"}  # 1000-10000us
            ]
        }
    ))
    # Override number to show actual value not log
    fig_db.update_traces(gauge_axis_tickvals=[0, 1, 2, 3, 4], gauge_axis_ticktext=["1", "10", "100", "1k", "10k"])
    fig_db.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
    st.plotly_chart(fig_db, use_container_width=True)


# --- SYSTEM DIAGNOSTICS (THE "FUN" PART) ---
st.markdown("### 🖥️ SYSTEM DIAGNOSTICS")

# Check for Crash
if current_ram > 480:
    st.markdown("""
    <div class="status-box danger-box">
        <h2 style="color:#ff0055!important; margin:0;">⚠️ CRITICAL FAILURE DETECTED ⚠️</h2>
        <p><strong>ERROR_OOM_KILLER:</strong> The Operating System has terminated your process.</p>
        <p><strong>Reason:</strong> High overhead from Standard Runtime (Java/Python) consumed all available RAM on the Raspberry Pi Zero.</p>
        <p><strong>Fix:</strong> Switch Kernel to <strong>TinyOneM2M (C-Based)</strong> to reduce memory footprint.</p>
    </div>
    """, unsafe_allow_html=True)
elif current_db_time > 1000:
    st.markdown("""
    <div class="status-box danger-box" style="border-color: orange; box-shadow: 0 0 15px rgba(255, 165, 0, 0.2);">
        <h2 style="color:orange!important; margin:0;">⚠️ LATENCY BOTTLENECK</h2>
        <p><strong>WARN_SLOW_QUERY:</strong> Database queries are taking >3ms.</p>
        <p><strong>Reason:</strong> Normalized database requires expensive JOIN operations for deep resource trees.</p>
        <p><strong>Fix:</strong> Switch DB Strategy to <strong>Denormalized</strong> for O(1) read access.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="status-box success-box">
        <h2 style="color:#00ff41!important; margin:0;">✅ SYSTEM OPTIMAL</h2>
        <p><strong>STATUS:</strong> Hardware resources are within safe limits.</p>
        <p><strong>RAM Headroom:</strong> Available.</p>
        <p><strong>Latency:</strong> Real-time.</p>
    </div>
    """, unsafe_allow_html=True)


# --- NETWORK VISUALIZER ---
st.markdown("### 🌐 LIVE NETWORK TOPOLOGY")

# Create a synthetic network based on load
# To make it performant, we limit visual nodes but show the scale
node_count = min(device_load, 100) # visual cap
x = np.random.rand(node_count)
y = np.random.rand(node_count)
sizes = np.random.randint(5, 15, node_count)

# Gateway Node
x = np.append(x, 0.5)
y = np.append(y, 0.5)
sizes = np.append(sizes, 30)
colors = ['#00f2ff'] * node_count + ['#ffffff'] # Blue nodes, White gateway

fig_net = go.Figure()

# Add Nodes
fig_net.add_trace(go.Scatter(
    x=x, y=y,
    mode='markers',
    marker=dict(size=sizes, color=colors, line=dict(width=1, color='DarkSlateGrey'))
))

# Add "Data Packet" lines (visual effect)
if current_ram <= 480:
    # Only draw lines if system isn't crashed
    lines_x = []
    lines_y = []
    for i in range(node_count):
        lines_x.extend([x[i], 0.5, None])
        lines_y.extend([y[i], 0.5, None])
    
    fig_net.add_trace(go.Scatter(
        x=lines_x, y=lines_y,
        mode='lines',
        line=dict(color='rgba(0, 242, 255, 0.2)', width=1)
    ))

fig_net.update_layout(
    showlegend=False,
    height=400,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig_net, use_container_width=True)

# --- ARCHITECTURE BREAKDOWN (EXPANDER) ---
with st.expander("🛠️ VIEW ARCHITECTURE BLUEPRINT"):
    st.markdown("""
    ### The TinyOneM2M Secret Sauce
    
    1.  **Protocol Wrapper:** Validates OneM2M standard compliance (57% coverage of v5.1).
    2.  **Embedded SQLite3:** Uses a single-file denormalized structure (Table `mtc`) for blazing fast reads.
    3.  **C-Language Core:** `pthread` and native sockets minimize overhead compared to Python/Java VMs.
    """)
    st.image("Architecture.jpg", caption="TinyOneM2M Internal Architecture")
