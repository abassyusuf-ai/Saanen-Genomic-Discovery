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
uploaded_file = st.file_uploader("📥 STEP 1: Upload 'Individual_Goat_Stats.txt'", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    try:
        # Load and handle column mismatch automatically
        df = pd.read_csv(uploaded_file, sep=None, engine='python', header=None, on_bad_lines='skip')
        
        # BCFtools standard names
        schema = ["Type", "ID", "Sample", "nHomRef", "nHet", "nHomAlt", "nMiss", "nSing", "Ti", "Tv", "Indels", "Depth", "M1", "M2", "M3"]
        df.columns = schema[:len(df.columns)] # Only use names for existing columns
        
        # Calculations
        df['TiTv'] = df['Ti'] / df['Tv']
        df['Selection_Index'] = df['nHomAlt'] / df['nHet'] # Higher = more stabilized traits

        st.success(f"✅ Ingestion Complete: {len(df)} Saanen samples ready for Exploration.")

        # --- PHASE 2: EXPLORATORY MODULES ---
        st.sidebar.header("🔬 Visual Controls")
        pub_mode = st.sidebar.checkbox("Nature Publication Mode")
        template = "plotly_white" if pub_mode else "plotly_dark"

        t1, t2, t3 = st.tabs(["🛡️ Quality Audit", "🎯 Selection Pressure", "📊 Population Diversity"])

        with t1:
            st.markdown("### Figure 1: Technical Integrity")
            fig1 = px.scatter(df, x="Depth", y="TiTv", color="nMiss", hover_name="Sample", template=template)
            fig1.add_hline(y=2.1, line_dash="dash", line_color="red", annotation_text="Ideal Ti/Tv")
            st.plotly_chart(fig1, use_container_width=True)

        with t2:
            st.markdown("### Figure 2: Lineage Stabilization")
            fig2 = px.scatter(df, x="nHet", y="nHomAlt", color="TiTv", size="Selection_Index", hover_name="Sample", template=template)
            st.plotly_chart(fig2, use_container_width=True)

        with t3:
            st.markdown("### Figure 3: Heterozygosity Spread")
            fig3 = px.violin(df, y="Selection_Index", box=True, points="all", template=template)
            st.plotly_chart(fig3, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Mapping Error: {e}")
else:
    st.info("👋 System Idle. Please upload your research data above to begin.")