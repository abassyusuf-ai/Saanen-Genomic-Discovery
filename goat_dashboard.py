import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="Genomic Research Workbench", layout="wide")
st.title("🧬 Advanced Genomic Discovery Suite")

uploaded_file = st.file_uploader("📥 Upload 'Individual_Goat_Stats.txt'", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    try:
        # 1. THE "PRECISION SURGERY" ON DATA
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        # We find the PSC lines and split them by any whitespace
        data = [line.split() for line in stringio if line.startswith("PSC")]
        
        # 2. ALIGNING COLUMNS (The reason your dots were at zero)
        # BCFtools PSC Order: [0]PSC, [1]ID, [2]Sample, [3]nHomRef, [4]nHet, [5]nHomAlt...
        df = pd.DataFrame(data)
        df = df[[2, 3, 4, 5, 8, 9, 11]] # Select: Sample, HomRef, Het, HomAlt, Ti, Tv, Depth
        df.columns = ["Sample", "nHomRef", "nHet", "nHomAlt", "Ti", "Tv", "Depth"]

        # 3. CONVERTING TO SCIENTIFIC NUMBERS
        for col in ["nHomRef", "nHet", "nHomAlt", "Ti", "Tv", "Depth"]:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 4. CALCULATING METRICS
        df['TiTv'] = df['Ti'] / df['Tv']
        df['Heterozygosity_Rate'] = df['nHet'] / (df['nHomRef'] + df['nHet'] + df['nHomAlt'])
        df = df.dropna()

        st.success(f"✅ Protocol Active: {len(df)} Saanen genomes mapped.")

        # --- REPLICATING THE RESEARCH FIGURES ---
        tab1, tab2, tab3 = st.tabs(["📊 Population Structure", "🛡️ Quality Audit", "🎯 Variant Discovery"])

        with tab1:
            st.markdown("### Population Heterozygosity (Similar to Fig 1a in your reference)")
            # This replicates the "Violin/Density" style of the Nature paper
            fig_pop = px.violin(df, y="Heterozygosity_Rate", box=True, points="all", 
                               hover_name="Sample", color_discrete_sequence=["#BB5566"],
                               template="plotly_dark", title="Heterozygosity Distribution across Herd")
            st.plotly_chart(fig_pop, use_container_width=True)

        with tab2:
            st.markdown("### Technical Integrity (Ti/Tv Standards)")
            fig_ti = px.histogram(df, x="TiTv", nbins=30, template="plotly_dark",
                                 title="Ti/Tv Ratio Histogram (Expected Peak at 2.1)")
            fig_ti.add_vline(x=2.1, line_dash="dash", line_color="red")
            st.plotly_chart(fig_ti, use_container_width=True)

        with tab3:
            st.markdown("### Stabilization Map (The 'Discovery' Plot)")
            # Replicating the scatter analysis to find medicinal founder candidates
            fig_disc = px.scatter(df, x="nHet", y="nHomAlt", color="TiTv", size="Depth",
                                 hover_name="Sample", template="plotly_dark",
                                 color_continuous_scale="Viridis")
            st.plotly_chart(fig_disc, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Alignment Error: {e}")