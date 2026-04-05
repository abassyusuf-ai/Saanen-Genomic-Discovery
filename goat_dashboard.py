import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Genomic Research Workbench", layout="wide")
st.title("🧬 Genomic Research Workbench")

uploaded_file = st.file_uploader("📥 Upload 'Individual_Goat_Stats.txt'", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    try:
        # 1. Read the file, skipping any lines that aren't the sample data
        # We use 'comment' to ignore the metadata lines starting with #
        df = pd.read_csv(uploaded_file, sep="\t", comment='#', header=None, engine='python')
        
        # 2. CRITICAL FILTER: BCFtools individual stats always start with 'PSC'
        # This removes any summary rows that aren't about the individual goats
        df = df[df[0] == "PSC"]

        # 3. Apply the 14-column Schema
        schema = ["Type", "ID", "Sample", "nHomRef", "nHet", "nHomAlt", "nMiss", "nSing", "Ti", "Tv", "Indels", "Depth", "M1", "M2"]
        df.columns = schema[:len(df.columns)]

        # 4. Convert to Numbers (Force conversion)
        cols_to_fix = ["nHomRef", "nHet", "nHomAlt", "nMiss", "Ti", "Tv", "Depth"]
        for col in cols_to_fix:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 5. Calculations
        df['TiTv'] = df['Ti'] / df['Tv']
        df = df.dropna(subset=['TiTv']) # Remove any remaining broken rows

        if len(df) > 0:
            st.success(f"✅ Analysis Active: {len(df)} Saanen samples identified.")
            
            t1, t2 = st.tabs(["🛡️ Quality Audit", "🎯 Selection Pressure"])
            with t1:
                st.markdown("### Figure 1: Technical Integrity (Ti/Tv)")
                fig1 = px.scatter(df, x="Depth", y="TiTv", color="nMiss", hover_name="Sample", template="plotly_dark")
                fig1.add_hline(y=2.1, line_dash="dash", line_color="red", annotation_text="Ideal Ti/Tv")
                st.plotly_chart(fig1, use_container_width=True)

            with t2:
                st.markdown("### Figure 2: Lineage Stabilization")
                fig2 = px.scatter(df, x="nHet", y="nHomAlt", color="TiTv", size="Depth", hover_name="Sample", template="plotly_dark")
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.error("❌ No sample data (PSC rows) found in the file. Please check your bcftools output.")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")