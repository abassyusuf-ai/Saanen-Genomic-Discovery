import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Nature Style Guide
N_COLORS = ["#004488", "#DDAA33", "#BB5566", "#000000"]

st.set_page_config(page_title="Saanen Genomic Discovery Hub", layout="wide")

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4259; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER SECTION ---
st.title("🧬 Saanen Genomic Discovery Hub")
st.subheader("Medicinal Lineage Stabilization & Variant Analysis")

# --- PHASE 2: THE UPLOAD GATE ---
with st.expander("📂 STEP 1: Initialize Research Environment", expanded=True):
    col_a, col_b = st.columns([2, 1])
    with col_a:
        uploaded_file = st.file_uploader("Upload 'Individual_Goat_Stats.txt' from your local machine", type=['txt', 'csv', 'tsv'])
    with col_b:
        st.info("💡 **Required Format:** BCFtools PSC output containing Zygosity, Ti/Tv, and Depth metrics.")

# --- RESEARCH EXPLORATION ENGINE ---
if uploaded_file is not None:
    try:
        # Load and map columns
        df = pd.read_csv(uploaded_file, sep=None, engine='python', header=None, on_bad_lines='skip')
        df.columns = ["Type", "ID", "Sample", "nHomRef", "nHet", "nHomAlt", "nMiss", "nSing", "Ti", "Tv", "Indels", "Depth", "Misc1", "Misc2"]
        df['TiTv'] = df['Ti'] / df['Tv']
        
        # Sidebar Settings
        st.sidebar.header("⚙️ Analysis Parameters")
        pub_mode = st.sidebar.checkbox("Nature Publication Mode")
        target_goat = st.sidebar.selectbox("Highlight Specific Sample", options=["None"] + list(df['Sample'].unique()))
        template = "plotly_white" if pub_mode else "plotly_dark"

        # --- EXPLORATION DASHBOARD ---
        st.divider()
        
        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Population Size", len(df))
        m2.metric("Mean Ti/Tv", round(df['TiTv'].mean(), 3))
        m3.metric("Highest HomAlt", df['nHomAlt'].max())
        m4.metric("Avg Depth", f"{int(df['Depth'].mean())}x")

        # Exploration Tabs
        tab1, tab2, tab3 = st.tabs(["📊 Quality Metrics", "🎯 Selection Pressure", "🧬 Sample Registry"])

        with tab1:
            st.markdown("#### Figure 1: Technical Integrity Audit")
            # Quality Control Exploration
            fig1 = px.scatter(df, x="Depth", y="TiTv", color="nMiss", 
                              template=template, size="nHomAlt",
                              title="Depth vs. Ti/Tv Ratio (Quality Check)")
            fig1.add_hline(y=2.1, line_dash="dash", line_color="red")
            st.plotly_chart(fig1, use_container_width=True)
            st.write("Researchers look for a tight cluster around 2.1 across all depths to confirm sequencing reliability.")

        with tab2:
            st.markdown("#### Figure 2: The 'Medicinal Gold' Search")
            # Discovering the outliers
            fig2 = px.scatter(df, x="nHet", y="nHomAlt", hover_name="Sample",
                              color="TiTv", size="Depth", template=template,
                              title="Zygosity Analysis: Identifying Stabilized Lineages")
            
            if target_goat != "None":
                selected = df[df['Sample'] == target_goat]
                fig2.add_annotation(x=selected['nHet'].values[0], y=selected['nHomAlt'].values[0],
                                    text=f"SELECTED: {target_goat}", showarrow=True, arrowhead=2)
            
            st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            st.markdown("#### Detailed Genomic Audit Table")
            st.dataframe(df.sort_values("nHomAlt", ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Error processing file: {e}")
else:
    # THE IDLE STATE
    st.image("https://images.unsplash.com/photo-1530026405186-ed1f139313f8?auto=format&fit=crop&q=80&w=1200", 
             caption="Waiting for Saanen Population Data...", use_container_width=True)
    st.info("System Ready. Please upload your research data to begin the exploration phase.")
