import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Nature/Cell Journal Standards
N_COLORS = ["#004488", "#DDAA33", "#BB5566", "#000000"]

st.set_page_config(page_title="Genomic Research Workbench", layout="wide")

st.title("🧬 Genomic Research Workbench")
st.markdown("#### Precision Lineage & Variant Discovery Suite")

# --- PHASE 1: THE IDLE GATE ---
uploaded_file = st.file_uploader("📥 STEP 1: Initialize Analysis by Uploading 'Individual_Goat_Stats.txt'", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    try:
        # Load and clean (Handling the 14-column structure)
        df = pd.read_csv(uploaded_file, sep=None, engine='python', header=None, on_bad_lines='skip')
        
        # CALIBRATED 14-COLUMN MAPPING
        # Mapping: Type, ID, Sample, nHomRef, nHet, nHomAlt, nMiss, nSing, Ti, Tv, Indels, Depth, Misc1, Misc2
        # If your file has 14 columns, we map them directly:
        cols = ["Type", "ID", "Sample", "nHomRef", "nHet", "nHomAlt", "nMiss", "nSing", "Ti", "Tv", "Indels", "Depth", "M1", "M2"]
        df.columns = cols[:len(df.columns)] 
        
        # --- PHASE 2: EXPLORATORY DATA ANALYSIS (EDA) ---
        df['TiTv'] = df['Ti'] / df['Tv']
        df['Quality_Score'] = (df['Depth'] * df['TiTv']) / 2.1 # Custom Research Metric
        
        st.success(f"✅ Ingestion Complete: {len(df)} Saanen samples mapped for exploration.")

        st.sidebar.header("🔬 Visual Controls")
        pub_mode = st.sidebar.checkbox("Enable Nature Publication Mode")
        template = "plotly_white" if pub_mode else "plotly_dark"

        tab1, tab2, tab3 = st.tabs(["🛡️ Quality Audit", "🎯 Selection Pressure", "📋 Data Registry"])

        with tab1:
            st.markdown("### Module 1: Technical Integrity Audit")
            st.write("Does sequencing depth influence our variant quality? (Checking for bias)")
            fig1 = px.scatter(df, x="Depth", y="TiTv", color="nMiss", 
                              hover_name="Sample", template=template,
                              title="Depth vs. Ti/Tv (Biological Stability Check)")
            fig1.add_hline(y=2.1, line_dash="dash", line_color="red", annotation_text="Ideal: 2.1")
            st.plotly_chart(fig1, use_container_width=True)
            

        with tab2:
            st.markdown("### Module 2: The 'Stabilized Lineage' Search")
            st.write("We are looking for 'Top Right' outliers: High Homozygosity for medicinal trait fixing.")
            fig2 = px.scatter(df, x="nHet", y="nHomAlt", color="TiTv", 
                              size="Depth", hover_name="Sample", template=template,
                              title="Zygosity Exploration: Finding the Genetic Gold")
            st.plotly_chart(fig2, use_container_width=True)
            

        with tab3:
            st.markdown("### Module 3: Raw Exploratory Table")
            st.dataframe(df.sort_values("nHomAlt", ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Mapping Error: {e}")
        st.info("Tip: Ensure your file was generated using 'bcftools stats' on your VCF.")

else:
    # --- IDLE STATE ---
    st.info("👋 System Ready. Awaiting data for exploratory analysis.")
    st.markdown("""
    **Exploratory Benefits of this Workbench:**
    1.  **Validation:** Instant Ti/Tv calculation to prove your 41GB data isn't corrupted.
    2.  **Discovery:** High-speed outlier detection for medicinal goat candidates.
    3.  **Audit:** Full population table for one-click candidate sorting.
    """)
