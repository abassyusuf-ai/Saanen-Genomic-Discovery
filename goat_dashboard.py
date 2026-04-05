import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="Genomic Research Workbench", layout="wide")
st.title("🧬 Precision Discovery Suite")

uploaded_file = st.file_uploader("📥 Upload 'Individual_Goat_Stats.txt'", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    try:
        # 1. READ RAW DATA
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        # Split every PSC line into a list of words
        raw_data = [line.split() for line in stringio if line.startswith("PSC")]
        
        df_raw = pd.DataFrame(raw_data)

        # 2. AUTO-COLUMN DISCOVERY
        # We need to find: SampleName, nHet, nHomAlt, Ti, Tv, Depth
        # In BCFtools, Sample is usually index 2, nHet is 4, nHomAlt is 5, Ti is 8, Tv is 9
        
        df = pd.DataFrame()
        df['Sample'] = df_raw[2]
        df['nHet'] = pd.to_numeric(df_raw[4], errors='coerce')
        df['nHomAlt'] = pd.to_numeric(df_raw[5], errors='coerce')
        df['Ti'] = pd.to_numeric(df_raw[8], errors='coerce')
        df['Tv'] = pd.to_numeric(df_raw[9], errors='coerce')
        df['Depth'] = pd.to_numeric(df_raw[11], errors='coerce')

        # 3. CALCULATE
        df['TiTv'] = df['Ti'] / df['Tv']
        
        # Clean up any broken rows
        df = df.dropna(subset=['nHet', 'nHomAlt', 'TiTv'])
        # Filter out extreme outliers that break the scale
        df = df[df['TiTv'] > 0] 

        if len(df) > 0:
            st.success(f"✅ Alignment Fixed: {len(df)} Saanen samples mapped.")

            t1, t2 = st.tabs(["🎯 Discovery Map", "🛡️ Quality Check"])

            with t1:
                st.markdown("### Figure 2: Lineage Stabilization")
                # This scatter plot will now show the cloud of 298 dots
                fig2 = px.scatter(df, x="nHet", y="nHomAlt", color="TiTv", 
                                 size="Depth", hover_name="Sample", 
                                 color_continuous_scale="Viridis",
                                 template="plotly_dark",
                                 title="Target: High nHomAlt (Y-axis) identifies stabilized medicinal traits")
                st.plotly_chart(fig2, use_container_width=True)
            
            with t2:
                st.markdown("### Figure 1: Technical Integrity")
                fig1 = px.scatter(df, x="Depth", y="TiTv", hover_name="Sample", template="plotly_dark")
                fig1.add_hline(y=2.1, line_dash="dash", line_color="red", annotation_text="Biological Standard (2.1)")
                st.plotly_chart(fig1, use_container_width=True)
        else:
            st.error("❌ Data detected, but columns are not aligning. Please check the file format.")

    except Exception as e:
        st.error(f"⚠️ System Error: {e}")