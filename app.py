import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import random

# --- PAGE CONFIGURATION (The Canvas) ---
st.set_page_config(
    page_title="TinyOneM2M: Edge Ops",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM "CYBER-HUD" CSS ---
st.markdown("""
<style>
    /* Dark Theme Base */
    .stApp {
        background-color: #0e1117;
        color: #c9d1d9;
    }
    
    /* Neon Glow Headers */
    h1, h2, h3 {
        font-family: 'Courier New', monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    h1 {
        background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        text-shadow: 0px 0px 20px rgba(0, 210, 255, 0.3);
    }

    /* Metric Cards - HUD Style */
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #333;
        transition: all 0.3s ease;
    }
    
    /* Dynamic Border Colors for Metrics */
    div[data-testid="metric-container"]:hover {
        border-left: 5px solid #00d2ff;
        box-shadow: 0 0 20px rgba(0, 210, 255, 0.2);
    }

    /* Custom Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 0px;
        border: 1px solid #00d2ff;
        color: #00d2ff;
        background: transparent;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background: #00d2ff;
        color: #000;
        box-shadow: 0 0 15px #00d2ff;
    }

    /* Console Log Styling */
    .console-log {
        font-family: 'Courier New', monospace;
        font-size: 12px;
        background-color: #000;
        color: #00ff00;
        padding: 10px;
        border: 1px solid #333;
        height: 150px;
        overflow-y: scroll;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'log_history' not in st.session_state:
    st.session_state.log_history = ["> SYSTEM INITIALIZED...", "> WAITING FOR INPUT..."]
if 'system_status' not in st.session_state:
    st.session_state.system_status = "IDLE"

# --- HELPER FUNCTIONS ---
def add_log(message):
    st.session_state.log_history.append(f"> {time.strftime('%H:%M:%S')} | {message}")
    if len(st.session_state.log_history) > 8:
        st.session_state.log_history.pop(0)

# --- SIDEBAR: MISSION CONFIGURATION ---
with st.sidebar:
    st.title("⚙️ OPS CONFIG")
    st.markdown("---")
    
    st.subheader("1. HARDWARE TARGET")
    hw_profile = st.selectbox(
        "Device Profile",
        ["Raspberry Pi Zero W (512MB)", "Generic Gateway (4GB)", "Cloud Instance (16GB)"],
        index=0,
        help="Section V-E: Minimal Hardware Compatibility Testing"
    )
    
    st.subheader("2. ARCHITECTURE")
    db_strategy = st.radio(
        "Database Strategy",
        ["Normalized (Standard)", "Denormalized (TinyOneM2M)"],
        index=1,
        help="Section V-A: Denormalization reduces Deep Query time from 3300us to 4.5us."
    )
    
    runtime_type = st.radio(
        "Runtime Core",
        ["Python/Java (OpenMTC)", "C-Native (TinyOneM2M)"],
        index=1,
        help="Section IV: C uses pthreads and native sockets for low overhead."
    )
    
    st.markdown("---")
    st.info("💡 **TIP:** Toggle the **Database Strategy** during simulation to see the latency collapse instantly.")

# --- MAIN DASHBOARD ---

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("TINY-ONEM2M // EDGE COMMANDER")
    st.markdown("**IMPLEMENTATION OF IEEE DSIT 2024 STANDARD (v5.1)**")
with col2:
    st.markdown(f"<div style='text-align:right; font-family:monospace; color:#00d2ff;'>STATUS: {st.session_state.system_status}<br>TARGET: {hw_profile.split('(')[0]}</div>", unsafe_allow_html=True)

# --- LIVE SIMULATION ENGINE ---
# We use a placeholder container to update metrics dynamically
placeholder = st.empty()
run_sim = st.checkbox("🟢 ACTIVATE NETWORK SIMULATION", value=False)

if run_sim:
    st.session_state.system_status = "ONLINE"
    
    # Simulation Loop
    for i in range(100):
        # 1. CALCULATE METRICS BASED ON PAPER DATA
        
        # Load Factor (Randomized slightly)
        load_factor = np.random.normal(1.0, 0.1)
        
        # A. Latency Calculation (Section V-C & V-A)
        # Normalized DB is EXPONENTIALLY slower on deep queries
        if db_strategy == "Normalized (Standard)":
            base_latency = 3300.0 * load_factor # microseconds (Table VI)
            latency_color = "inverse" # Red
        else:
            base_latency = 4.5 * load_factor # microseconds (Table VI)
            latency_color = "normal" # Green
            
        # Add Runtime Overhead (Java/Python vs C)
        # Table VIII: OpenMTC max latency 15ms vs TinyOneM2M 1.1ms
        if runtime_type == "Python/Java (OpenMTC)":
            runtime_overhead = np.random.randint(5000, 15000) # us
            mem_usage_base = 60 # MB
        else:
            runtime_overhead = np.random.randint(100, 1200) # us
            mem_usage_base = 5 # MB
            
        total_latency_ms = (base_latency + runtime_overhead) / 1000.0
        
        # B. RAM Calculation (Section V-E Table IX)
        # 100k resources = ~14MB RAM for TinyOneM2M
        resource_count = 10000 + (i * 1000)
        if runtime_type == "C-Native (TinyOneM2M)":
            ram_usage = mem_usage_base + (resource_count * 0.00014) # Approx slope from Table IX
        else:
            ram_usage = mem_usage_base + (resource_count * 0.0008) # Higher slope for managed languages
            
        # C. Crash Logic for Pi Zero (512MB Limit)
        is_crashed = False
        if "Zero" in hw_profile and ram_usage > 450:
            is_crashed = True
            st.session_state.system_status = "CRITICAL MEMORY"
        
        # 2. RENDER UI
        with placeholder.container():
            # A. Key Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Active Resources", f"{resource_count:,}", delta="+1000/s")
            m2.metric("Query Latency", f"{total_latency_ms:.2f} ms", delta=f"{'HIGH' if total_latency_ms > 10 else 'OPTIMAL'}", delta_color=latency_color)
            m3.metric("RAM Usage", f"{ram_usage:.1f} MB", delta=f"{ram_usage/512*100:.1f}% Capacity", delta_color="inverse" if ram_usage > 400 else "normal")
            m4.metric("Thread Pool", "Active", delta="Native Pthreads" if "C-Native" in runtime_type else "JVM Threads")

            # B. Visualizers
            c_chart, c_log = st.columns([2, 1])
            
            with c_chart:
                # Latency Strip Chart
                chart_data = pd.DataFrame({
                    'Time': range(i), 
                    'Latency (ms)': [total_latency_ms + np.random.uniform(-0.5, 0.5) for _ in range(i)]
                })
                st.line_chart(chart_data, y='Latency (ms)', height=200)
                
                # Critical Warning
                if is_crashed:
                    st.error("⚠️ SYSTEM FAILURE: OUT OF MEMORY (OOM KILLER TRIGGERED)")
                    st.markdown("Standard Runtimes cannot sustain >100k resources on Pi Zero. Switch to **TinyOneM2M**.")
                    break
                
                if total_latency_ms > 10:
                    st.warning("⚠️ HIGH LATENCY DETECTED: Switch DB Strategy to **Denormalized** to optimize SELECT queries.")

            with c_log:
                # Simulated Console Output based on Architecture
                action = random.choice(["INSERT CIN", "RETRIEVE AE", "DISCOVERY", "NOTIFY SUB"])
                add_log(f"{action} >> {runtime_type.split()[0]} >> DB: {db_strategy.split()[0]} >> {total_latency_ms:.2f}ms")
                
                log_html = "<div class='console-log'>" + "<br>".join(st.session_state.log_history) + "</div>"
                st.markdown(log_html, unsafe_allow_html=True)
        
        time.sleep(0.1) # Refresh rate
        
else:
    # --- STATIC VIEW (When Sim is Off) ---
    with placeholder.container():
        st.info("👆 ACTIVATE SIMULATION TO START STRESS TESTING")
        
        # Show Architecture Diagram when Idle
        st.markdown("### 🏗️ SYSTEM ARCHITECTURE BLUEPRINT")
        st.caption("Visualizing the C-Based Threading Model (Section III-B)")
        
        st.graphviz_chart('''
            digraph {
                rankdir=LR;
                bgcolor="#0e1117";
                node [style=filled, fillcolor="#1f2937", fontcolor="white", fontname="Courier New", shape=box, color="#374151"];
                edge [color="#00d2ff", penwidth=1.5];

                Client [label="IoT Device\n(HTTP/CoAP)", shape=ellipse, fillcolor="#00d2ff", fontcolor="black"];
                
                subgraph cluster_tiny {
                    label = "TinyOneM2M Core (C)";
                    style = dashed;
                    color = "#4b5563";
                    fontcolor = "#9ca3af";
                    
                    Router [label="1. Socket Listener\n(Native)", color="#10b981"];
                    Worker [label="2. Thread Pool\n(pthread)", color="#f59e0b"];
                    Logic [label="3. Protocol Wrapper\n(OneM2M v5.1)"];
                    
                    subgraph cluster_db {
                        label = "Persistence";
                        bgcolor = "#111827";
                        DB [label="SQLite3\n(Denormalized)", shape=cylinder, fillcolor="#ec4899"];
                    }
                }
                
                Client -> Router [label="REST"];
                Router -> Worker [label="Spawn"];
                Worker -> Logic [label="Process"];
                Logic -> DB [label="Fast I/O"];
            }
        ''')

# --- DATA DEEP DIVES ---
st.markdown("---")
st.header("📊 RESEARCH DATA VAULT")

tab1, tab2, tab3 = st.tabs(["DB PERFORMANCE (Table VI)", "LATENCY BENCHMARK (Table VIII)", "RESOURCE SCALING (Table IX)"])

with tab1:
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("""
        **The Problem:** In a standard normalized DB (many tables), retrieving a deep child resource (e.g., `/CSE/AE/CNT/CIN`) requires multiple expensive `JOIN` operations.
        
        **The TinyOneM2M Solution:** We use a **Denormalized** single-table structure.
        
        **Result:** `SELECT` operation time drops from **3300 μs** to **4.5 μs**.
        """)
    with col_t2:
        # Visualizing Table VI
        ops = ['Insert', 'Select (Deep)', 'Update', 'Delete']
        norm_times = [7.0, 3300.0, 7.0, 3.8]
        denorm_times = [6.96, 4.5, 6.9, 3.6]
        
        fig_db = go.Figure(data=[
            go.Bar(name='Normalized', x=ops, y=norm_times, marker_color='#ef4444'),
            go.Bar(name='Denormalized (Tiny)', x=ops, y=denorm_times, marker_color='#00d2ff')
        ])
        fig_db.update_layout(
            title="Execution Time (Log Scale) - Lower is Better",
            yaxis_type="log",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="white"
        )
        st.plotly_chart(fig_db, use_container_width=True)

with tab2:
    st.markdown("""
    Comparing **TinyOneM2M (C)** vs **OpenMTC (Python)**. 
    Notice the **Max Latency** spikes in OpenMTC (up to 15ms) caused by Garbage Collection and VM overhead, whereas TinyOneM2M remains stable near 1ms.
    """)
    # Data from Table VIII
    ops_lat = ['POST', 'GET', 'PUT', 'DELETE']
    tiny_max = [1.14, 0.11, 0.59, 0.54]
    open_max = [15.60, 1.07, 0.14, 0.05]
    
    fig_lat = go.Figure()
    fig_lat.add_trace(go.Scatter(x=ops_lat, y=tiny_max, name='TinyOneM2M Max', line=dict(color='#00d2ff', width=4)))
    fig_lat.add_trace(go.Scatter(x=ops_lat, y=open_max, name='OpenMTC Max', line=dict(color='#ef4444', width=4, dash='dot')))
    
    fig_lat.update_layout(
        title="Maximum Latency Stability (ms)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white"
    )
    st.plotly_chart(fig_lat, use_container_width=True)

with tab3:
    st.markdown("""
    **The Pi Zero Test:** Creating 100,000 Content Instances (CIN) on a device with 512MB RAM.
    TinyOneM2M uses only **14.7 MB** of RAM for 100k resources, leaving plenty of room for applications.
    """)
    # Data from Table IX
    resources = [10000, 50000, 100000]
    ram_usage = [5.6, 9.6, 14.7] # MB
    
    fig_ram = px.area(
        x=resources, y=ram_usage, 
        labels={'x':'Resources Created', 'y':'RAM Usage (MB)'},
        color_discrete_sequence=['#10b981']
    )
    fig_ram.update_layout(
        title="RAM Usage Growth (Linear & Efficient)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white"
    )
    st.plotly_chart(fig_ram, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>TINY-ONEM2M RESEARCH DEMO | IEEE DSIT 2024 | AUTHOR: SHUJAATALI BADAMI</small>
</div>
""", unsafe_allow_html=True)
