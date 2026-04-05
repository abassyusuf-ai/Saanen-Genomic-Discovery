import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Nature/Cell Journal Standards
N_COLORS = ["#004488", "#DDAA33", "#BB5566", "#000000"]

st.set_page_config(page_title="Genomic Research Workbench", layout="wide")

st.title("🧬 Genomic Research Workbench")
st.markdown("#### Precision Lineage & Variant Discovery Suite")

uploaded_file = st.file_uploader("📥 STEP 1: Upload 'Individual_Goat_Stats.txt'", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    try:
        # Load data
        df = pd.read_csv(uploaded_file, sep=None, engine='python', header=None, on_bad_lines='skip')
        
        # 1. Flexible Schema Mapping
        schema = ["Type", "ID", "Sample", "nHomRef", "nHet", "nHomAlt", "nMiss", "nSing", "Ti", "Tv", "Indels", "Depth", "M1", "M2", "M3"]
        df.columns = schema[:len(df.columns)]

        # 2. THE CRITICAL FIX: Convert strings to numbers
        # We force numeric conversion for the columns used in calculations
        cols_to_fix = ["Ti", "Tv", "nHet", "nHomAlt", "Depth", "nMiss"]
        for col in cols_to_fix:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 3. Clean the Data: Drop rows that aren't numeric (like headers)
        df = df.dropna(subset=["Ti", "Tv", "nHet", "nHomAlt"])

        # 4. Perform the calculation (Now it works!)
        df['TiTv'] = df['Ti'] / df['Tv']
        df['Selection_Index'] = df['nHomAlt'] / df['nHet']

        st.success(f"✅ Ingestion Complete: {len(df)} Saanen samples ready for Exploration.")

        # --- EXPLORATORY MODULES ---
        st.sidebar.header("🔬 Visual Controls")
        template = "plotly_white" if st.sidebar.checkbox("Nature Publication Mode") else "plotly_dark"

        t1, t2 = st.tabs(["🛡️ Quality Audit", "🎯 Selection Pressure"])

        with t1:
            st.markdown("### Figure 1: Technical Integrity (Ti/Tv)")
            fig1 = px.scatter(df, x="Depth", y="TiTv", color="nMiss", hover_name="Sample", template=template)
            fig1.add_hline(y=2.1, line_dash="dash", line_color="red", annotation_text="Ideal Ti/Tv")
            st.plotly_chart(fig1, use_container_width=True)

        with t2:
            st.markdown("### Figure 2: Lineage Stabilization")
            # This identifies the "Gold" goats for your medicinal traits
            fig2 = px.scatter(df, x="nHet", y="nHomAlt", color="TiTv", size="Depth", hover_name="Sample", template=template)
            st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Data Type Error: {e}")
else:
    st.info("👋 System Ready. Please upload your research data above to begin.")