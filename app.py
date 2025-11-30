import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TinyOneM2M: Lightweight IoT Standard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR "WOW" FACTOR ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #475569;
        font-style: italic;
    }
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f1f5f9;
        border-radius: 4px;
        color: #64748b;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #00d2ff;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="main-header">📡 Efficient OneM2M for Lightweight IoT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Implementing the Standard on Constrained Edge Devices</div>', unsafe_allow_html=True)
    st.markdown("**Author:** Shujaatali Badami | **Venue:** IEEE DSIT 2024")
with col_h2:
    st.markdown('<div style="text-align: right;">', unsafe_allow_html=True)
    st.markdown('<img src="https://img.shields.io/badge/Project-TinyOneM2M-00d2ff?style=for-the-badge" width="180">', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR: SIMULATION CONFIG ---
with st.sidebar:
    st.header("🎛️ IoT Network Config")
    st.markdown("Simulate the load on your **TinyOneM2M** gateway.")
    
    device_count = st.slider("Number of IoT Devices", 100, 10000, 1000, step=100)
    msg_freq = st.slider("Messages per Minute (per Device)", 1, 60, 10)
    
    st.subheader("Hardware Profile")
    hw_type = st.selectbox("Target Device", ["Raspberry Pi Zero W", "Raspberry Pi 3B+", "Generic Microcontroller"])
    
    total_load = device_count * msg_freq
    st.metric("Total Load", f"{total_load:,} req/min", delta="High Traffic" if total_load > 20000 else "Normal")

# --- TABS ---
tab_arch, tab_perf, tab_sim = st.tabs(["🏗️ Architecture & Stack", "⚡ Performance Benchmarks", "💾 Resource Simulator"])

# =======================================================
# TAB 1: ARCHITECTURE
# =======================================================
with tab_arch:
    st.subheader("The TinyOneM2M Architecture")
    st.markdown("""
    The system is designed to be **lightweight**, **portable**, and **efficient**, using C-based modules to handle the OneM2M standard resource tree (CSE, AE, CNT, CIN, SUB).
    """)

    col_diag, col_info = st.columns([2, 1])

    with col_diag:
        # Architecture Visualization based on Fig 2 of the paper
        st.graphviz_chart('''
            digraph {
                rankdir=LR;
                bgcolor="transparent";
                node [shape=box style="filled,rounded" fontname="Helvetica" penwidth=0];
                edge [fontname="Helvetica" color="#94a3b8" penwidth=1.5];

                subgraph cluster_external {
                    label = "External World";
                    style=dashed;
                    color="#cbd5e1";
                    fontcolor="#64748b";
                    Client [label="IoT Device / App" fillcolor="#e0f2fe" fontcolor="#0369a1"];
                    Broker [label="MQTT Broker" fillcolor="#f1f5f9" fontcolor="#475569"];
                }

                subgraph cluster_tiny {
                    label = "TinyOneM2M (C-Implementation)";
                    style=filled;
                    color="#f8fafc";
                    fillcolor="#f8fafc";
                    fontcolor="#0f172a";
                    
                    REST [label="1. WebService\nREST" fillcolor="#00d2ff" fontcolor="white"];
                    Processor [label="2. Response\nProcessor" fillcolor="#334155" fontcolor="white"];
                    Wrapper [label="3. Protocol\nWrapper" fillcolor="#475569" fontcolor="white"];
                    Resources [label="4. M2M\nResources" fillcolor="#0f172a" fontcolor="white"];
                    DB [label="SQLite3\n(Embedded)" shape=cylinder fillcolor="#fbbf24" fontcolor="#78350f"];
                    Notif [label="Notification\nModule" fillcolor="#22c55e" fontcolor="white"];
                }

                Client -> REST [label="HTTP (CRUD)"];
                REST -> Processor [label="New Thread"];
                Processor -> Wrapper [label="Parse"];
                Wrapper -> Resources [label="Validate"];
                Resources -> DB [label="Persist"];
                Resources -> Notif [label="Trigger SUB"];
                Notif -> Broker [label="Publish"];
            }
        ''')

    with col_info:
        st.info("**Key Design Choices**")
        st.markdown("""
        * **Language:** C (Low-level memory control)
        * **Concurrency:** `pthread` for non-blocking I/O.
        * **Database:** Embedded SQLite3 (Zero config).
        * **Network:** Native Sockets for minimal overhead.
        """)
        
        scenario = st.radio("Deployment Scenario", ["Home Gateway", "Peer-to-Peer (P2P)", "Cloud"], index=0)
        if scenario == "Home Gateway":
            st.caption("Centralized hub managing local devices (Zigbee/WiFi) before sending to cloud.")
        elif scenario == "Peer-to-Peer (P2P)":
            st.caption("Direct device-to-device communication without a central broker.")
        else:
            st.caption("Horizontally scaled instances behind a Load Balancer.")

# =======================================================
# TAB 2: PERFORMANCE
# =======================================================
with tab_perf:
    st.subheader("Benchmarking vs. OpenMTC")
    
    # 1. LATENCY COMPARISON (Table VIII)
    st.markdown("### 1. Latency Face-off: TinyOneM2M vs OpenMTC")
    st.markdown("Comparing the execution time for standard operations. TinyOneM2M shows **lower maximum latency**, indicating better stability.")

    # Data from Table VIII
    latency_data = {
        'Operation': ['POST', 'POST', 'GET', 'GET', 'PUT', 'PUT', 'DELETE', 'DELETE'],
        'System': ['TinyOneM2M', 'OpenMTC', 'TinyOneM2M', 'OpenMTC', 'TinyOneM2M', 'OpenMTC', 'TinyOneM2M', 'OpenMTC'],
        'Max Latency (ms)': [1.14, 15.60, 0.11, 1.07, 0.12, 0.14, 0.12, 0.05],
        'Min Latency (ms)': [0.12, 0.01, 0.01, 0.01, 0.59, 0.01, 0.54, 0.01] 
    }
    df_lat = pd.DataFrame(latency_data)

    fig_lat = px.bar(
        df_lat, 
        x="Operation", 
        y="Max Latency (ms)", 
        color="System", 
        barmode="group",
        title="Stability Check: Maximum Latency (Lower is Better)",
        color_discrete_map={'TinyOneM2M': '#00d2ff', 'OpenMTC': '#94a3b8'}
    )
    st.plotly_chart(fig_lat, use_container_width=True)
    st.caption("*Note: While OpenMTC has lower minimums, TinyOneM2M avoids massive latency spikes (e.g., POST 15ms vs 1.14ms).*")

    st.markdown("---")

    # 2. DATABASE NORMALIZATION (Table VI)
    st.markdown("### 2. Database Strategy: Normalized vs Denormalized")
    st.markdown("The paper identified that **Denormalization** massively improves read performance for deep resource hierarchies.")

    col_db1, col_db2 = st.columns(2)
    
    with col_db1:
        # Data from Table VI
        db_data = pd.DataFrame({
            'Operation': ['Insert', 'Select (Deep)', 'Update', 'Delete'],
            'Normalized (us)': [7.0, 3300.0, 7.0, 3.8],
            'Denormalized (us)': [6.96, 4.5, 6.9, 3.6]
        })
        
        # Log scale for Select visualization because 3300 vs 4.5 is huge
        fig_db = go.Figure(data=[
            go.Bar(name='Normalized', x=db_data['Operation'], y=db_data['Normalized (us)'], marker_color='#ef4444'),
            go.Bar(name='Denormalized', x=db_data['Operation'], y=db_data['Denormalized (us)'], marker_color='#22c55e')
        ])
        fig_db.update_layout(title="Execution Time (Microseconds) - Log Scale", yaxis_type="log")
        st.plotly_chart(fig_db, use_container_width=True)
    
    with col_db2:
        st.success("**Insight:** Deep hierarchical queries (SELECT) in a normalized DB took **3,300 μs**. Denormalization reduced this to **4.5 μs**.")
        st.markdown("""
        * **Insert/Update/Delete:** Negligible difference.
        * **Select:** Orders of magnitude faster with Denormalization.
        * **Decision:** TinyOneM2M uses a single-table denormalized structure (SQLite3) for speed.
        """)

# =======================================================
# TAB 3: SIMULATOR
# =======================================================
with tab_sim:
    st.subheader("💾 Edge Hardware Resource Simulator")
    st.markdown("TinyOneM2M is built for devices like the **Raspberry Pi Zero W** (512MB RAM). See how it scales compared to heavier runtimes (Java/Python).")

    # --- INPUTS ---
    col_sim1, col_sim2 = st.columns([1, 2])
    
    with col_sim1:
        n_resources = st.slider("Number of Stored Resources (CIN)", 10_000, 200_000, 50_000, step=10_000)
        
        # Models based on Table IX
        # TinyOneM2M: ~0.1 KB RAM per resource (Slope from paper data)
        # Heavy Runtime: ~0.8 KB RAM per resource (Hypothetical standard overhead)
        
        # Baseline overhead
        base_tiny = 4000 # ~4MB base
        base_heavy = 60000 # ~60MB base (JVM/Python VM)
        
        # Per resource cost
        cost_tiny = 0.101 # KB
        cost_heavy = 0.6 # KB
        
        ram_tiny = (base_tiny + (n_resources * cost_tiny)) / 1024 # MB
        ram_heavy = (base_heavy + (n_resources * cost_heavy)) / 1024 # MB
        
        db_size = (n_resources * 0.9) / 1024 # Approx 0.9 KB disk per resource (Table IX)
    
    with col_sim2:
        # GAUGE CHARTS
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Database Size", f"{db_size:.1f} MB", help="Storage on SD Card")
        c2.metric("TinyOneM2M RAM", f"{ram_tiny:.1f} MB", delta="Lightweight", delta_color="normal")
        c3.metric("Standard Runtime RAM", f"{ram_heavy:.1f} MB", delta=f"+{(ram_heavy-ram_tiny):.1f} MB", delta_color="inverse")
        
        # Chart
        sim_df = pd.DataFrame({
            'Resource Count': list(range(10000, 210000, 10000)),
        })
        sim_df['TinyOneM2M (MB)'] = (base_tiny + (sim_df['Resource Count'] * cost_tiny)) / 1024
        sim_df['Standard (MB)'] = (base_heavy + (sim_df['Resource Count'] * cost_heavy)) / 1024
        
        fig_sim = px.line(sim_df, x='Resource Count', y=['TinyOneM2M (MB)', 'Standard (MB)'], 
                          title="Memory Scaling: C vs High-Level Languages",
                          color_discrete_map={'TinyOneM2M (MB)': '#00d2ff', 'Standard (MB)': '#ef4444'})
        
        # Add current selection point
        fig_sim.add_vline(x=n_resources, line_dash="dash", line_color="white")
        
        st.plotly_chart(fig_sim, use_container_width=True)
        
    st.info("""
    **Conclusion:** On a Raspberry Pi Zero (512MB RAM), a standard Java/Python runtime might crash or thrash swap space with >100k resources. 
    **TinyOneM2M** remains comfortably under 30MB, leaving room for the actual application logic.
    """)

# --- FOOTER ---
st.markdown("---")
st.caption("© 2025 Shujaatali Badami. Interactive implementation of research presented at IEEE DSIT 2024.")
