import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Nature Style Guide
N_COLORS = ["#004488", "#DDAA33", "#BB5566", "#000000"]

st.set_page_config(page_title="Genomic Research Workbench", layout="wide")

st.title("🧬 Genomic Research Workbench")
st.markdown("#### Precision Lineage & Variant Discovery Suite")

uploaded_file = st.file_uploader("📥 STEP 1: Upload 'Individual_Goat_Stats.txt'", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    try:
        # 1. Load data without headers first
        df = pd.read_csv(uploaded_file, sep=None, engine='python', header=None, on_bad_lines='skip')
        
        # 2. Define the standard BCFtools PSC column order
        full_schema = [
            "Type", "ID", "Sample", "nHomRef", "nHet", "nHomAlt", 
            "nMiss", "nSing", "Ti", "Tv", "Indels", "Depth", 
            "Misc1", "Misc2", "Misc3"
        ]
        
        # 3. DYNAMIC MAPPING: Only apply names for the columns that exist
        df.columns = full_schema[:len(df.columns)]
        
        # 4. Calculation (Basic Bio-Metrics)
        df['TiTv'] = df['Ti'] / df['Tv']
        
        st.success(f"✅ Ingestion Complete: {len(df)} samples mapped successfully.")

        # --- EXPLORATION MODULES ---
        tab1, tab2 = st.tabs(["🛡️ Quality Audit", "🎯 Selection Pressure"])

        with tab1:
            st.write("#### Figure 1: Ti/Tv Quality Distribution")
            fig1 = px.histogram(df, x="TiTv", nbins=50, template="plotly_dark")
            fig1.add_vline(x=2.1, line_dash="dash", line_color="red", annotation_text="Target: 2.1")
            st.plotly_chart(fig1, use_container_width=True)

        with tab2:
            st.write("#### Figure 2: Zygosity Outlier Analysis")
            fig2 = px.scatter(df, x="nHet", y="nHomAlt", hover_name="Sample", 
                              color="TiTv", size="Depth", template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Mapping Error: {e}")
else:
    st.info("System Ready. Please upload the stats file to begin exploration.")
