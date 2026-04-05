import streamlit as st
import pandas as pd
import plotly.express as px
import io
import re

st.set_page_config(page_title="Genomic Research Workbench", layout="wide")
st.title("🧬 Advanced Genomic Discovery Suite")

uploaded_file = st.file_uploader("📥 Upload 'Individual_Goat_Stats.txt'", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    try:
        # 1. READ RAW DATA
        raw_bytes = uploaded_file.getvalue().decode("utf-8")
        lines = raw_bytes.splitlines()

        # 2. EXTRACT PSC DATA WITHOUT FORCING HEADER MATCH
        psc_data = []
        for line in lines:
            if line.startswith("PSC"):
                # Split by tabs or multiple spaces
                parts = re.split(r'\t|\s+', line.strip())
                psc_data.append(parts)

        if not psc_data:
            st.error("❌ No PSC data found. Please check your file content.")
        else:
            # 3. CONVERT TO DATAFRAME
            df_raw = pd.DataFrame(psc_data)
            
            # 4. ROBUST MAPPING (Standard BCFtools Positions)
            # We map by position to bypass the 14 vs 15 element mismatch
            final_df = pd.DataFrame()
            
            # Standard BCFtools PSC Positions:
            # [2]=Sample, [3]=nHomRef, [4]=nHet, [5]=nHomAlt, [8]=Ti, [9]=Tv, [11]=AverageDepth
            try:
                final_df['Sample'] = df_raw[2]
                final_df['nHet'] = pd.to_numeric(df_raw[4], errors='coerce')
                final_df['nHomAlt'] = pd.to_numeric(df_raw[5], errors='coerce')
                final_df['Ti'] = pd.to_numeric(df_raw[8], errors='coerce')
                final_df['Tv'] = pd.to_numeric(df_raw[9], errors='coerce')
                final_df['Depth'] = pd.to_numeric(df_raw[11], errors='coerce')
            except KeyError:
                st.error("❌ The file structure is unexpected. Ensure this is an 'Individual Stats' file.")

            # 5. SCIENTIFIC CALCULATIONS
            final_df['TiTv'] = final_df['Ti'] / final_df['Tv']
            # Calculate Heterozygosity for the Nature-style Violin Plots
            total_vars = final_df['nHet'] + final_df['nHomAlt']
            final_df['Het_Rate'] = final_df['nHet'] / total_vars
            
            final_df = final_df.dropna(subset=['nHet', 'nHomAlt', 'TiTv'])

            # --- RESEARCH VISUALIZATION (MATCHING YOUR SHARED NATURE FIGURES) ---
            st.success(f"✅ Deep Sync Complete: {len(final_df)} Saanen Genomes Mapped.")

            tab1, tab2, tab3 = st.tabs(["📊 Population Structure", "🎯 Discovery Map", "🔬 Quality Audit"])

            with tab1:
                st.markdown("### Population Heterozygosity (Nature Fig 1/3 Style)")
                # Replicates the distribution plots from the research images you shared
                fig1 = px.violin(final_df, y="Het_Rate", box=True, points="all", 
                               hover_name="Sample", color_discrete_sequence=["#BB5566"],
                               template="plotly_dark", title="Heterozygosity Spread across 298 Goats")
                st.plotly_chart(fig1, use_container_width=True)

            with tab2:
                st.markdown("### Stabilization Map (Selection Pressure)")
                # High nHomAlt (Y-axis) = Fixed medicinal traits
                fig2 = px.scatter(final_df, x="nHet", y="nHomAlt", color="TiTv", 
                                 size="Depth", hover_name="Sample", 
                                 color_continuous_scale="Viridis", template="plotly_dark")
                st.plotly_chart(fig2, use_container_width=True)

            with tab3:
                st.markdown("### Technical Integrity (Ti/Tv Standards)")
                fig3 = px.histogram(final_df, x="TiTv", nbins=20, template="plotly_dark")
                fig3.add_hline(y=2.1, line_dash="dash", line_color="red", annotation_text="Biological Standard")
                st.plotly_chart(fig3, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ System Error: {e}")