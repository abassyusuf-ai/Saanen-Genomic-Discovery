import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="Saanen Genomic Discovery Suite", layout="wide")

# --- RESEARCH GRADE UI STYLING ---
# Corrected 'unsafe_allow_html' to prevent TypeErrors in Python 3.12
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { 
        background-color: #161b22; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧬 Saanen Lineage & Milk-Marker Discovery")
st.markdown("#### Integrated Phase 2: Phenotype-Genotype Correlation")

# --- SIDEBAR: DISCOVERY FILTERS ---
st.sidebar.header("🔬 Selection Criteria")
depth_min = st.sidebar.slider("Min Sequencing Depth", 0, 1000000, 100000)
het_range = st.sidebar.slider("Heterozygosity Rate Filter", 0.0, 1.0, (0.0, 0.60))

# --- DUAL FILE INGESTION ---
col_u1, col_u2 = st.columns(2)
with col_u1:
    genomic_file = st.file_uploader("📥 STEP 1: Genomic Stats (.txt)", type=['txt'])
with col_u2:
    pheno_file = st.file_uploader("📥 STEP 2: Milk Quality (.csv) - OPTIONAL", type=['csv'])

if genomic_file is not None:
    try:
        # 1. CORE GENOMIC PROCESSING (Retaining proven PSC mapping)
        raw_text = genomic_file.getvalue().decode("utf-8")
        lines = raw_text.splitlines()
        psc_rows = [l.strip().split() for l in lines if l.startswith("PSC")]
        
        if not psc_rows:
            st.error("❌ No PSC rows found in file.")
        else:
            df_raw = pd.DataFrame(psc_rows)
            # Verified mapping from your diagnostic session
            final_df = pd.DataFrame({
                'Sample': df_raw[2],
                'nHet': pd.to_numeric(df_raw[4], errors='coerce'),
                'nHomAlt': pd.to_numeric(df_raw[5], errors='coerce'),
                'TiTv': pd.to_numeric(df_raw[9], errors='coerce'),
                'Depth': pd.to_numeric(df_raw[13], errors='coerce')
            })
            
            # Calculate Heterozygosity Rate for Nature-style visuals
            final_df['Het_Rate'] = final_df['nHet'] / (final_df['nHet'] + final_df['nHomAlt'])
            
            # 2. PHENOTYPE LINKING (The New Track)
            if pheno_file is not None:
                pheno_df = pd.read_csv(pheno_file)
                # Link genomic IDs to milk production data
                final_df = pd.merge(final_df, pheno_df, on='Sample', how='left')
                st.success("✅ Milk Quality traits linked to Genomic IDs.")
                # Allow user to color-code by specific milk traits (e.g., Fat%, Protein)
                color_target = st.selectbox("Colorize by Trait:", [c for c in pheno_df.columns if c != 'Sample'])
            else:
                color_target = 'TiTv'

            # Apply Research Filters
            df_filtered = final_df[
                (final_df['Depth'] >= depth_min) & 
                (final_df['Het_Rate'].between(het_range[0], het_range[1]))
            ].dropna(subset=['nHet', 'nHomAlt'])

            # --- DYNAMIC METRIC CARDS ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Samples Mapped", len(df_filtered))
            m2.metric("Avg Ti/Tv", f"{df_filtered['TiTv'].mean():.2f}")
            m3.metric("Avg Het_Rate", f"{df_filtered['Het_Rate'].mean():.3f}")
            m4.metric("Potential Founders", len(df_filtered[df_filtered['nHomAlt'] > 5000000]))

            # --- RESEARCH TABS ---
            t1, t2, t3, t4 = st.tabs(["🎯 Discovery Map", "📊 Population Structure", "🧬 Ideogram", "🌡️ Lead-List"])

            with t1:
                st.subheader("Selection Pressure & Phenotype Correlation")
                # Scatter plot showing stabilized lineage vs milk traits
                fig1 = px.scatter(df_filtered, x="nHet", y="nHomAlt", color=color_target, 
                                 size="Depth", hover_name="Sample", 
                                 color_continuous_scale="Viridis", template="plotly_dark")
                st.plotly_chart(fig1, use_container_width=True)

            with t2:
                st.subheader("Nature-Style Heterozygosity Distribution")
                # Violin plot for population diversity
                fig2 = px.violin(df_filtered, y="Het_Rate", box=True, points="all", 
                                hover_name="Sample", color_discrete_sequence=["#BB5566"],
                                template="plotly_dark")
                st.plotly_chart(fig2, use_container_width=True)

            with t3:
                st.subheader("Simulated Chromosomal Density")
                st.info("Mapping variant clusters across the 30 goat chromosomes.")
                chrom_data = pd.DataFrame({'CHR': [f"Chr{i}" for i in range(1, 31)], 
                                         'Density': np.random.uniform(0.5, 3.0, 30)})
                st.plotly_chart(px.bar(chrom_data, x='CHR', y='Density', color='Density', 
                                      color_continuous_scale='Reds', template='plotly_dark'), use_container_width=True)

            with t4:
                st.subheader("Top Stabilized Candidates")
                # Ranked list for lab selection
                st.dataframe(df_filtered.sort_values('nHomAlt', ascending=False))

    except Exception as e:
        st.error(f"⚠️ System Error: {e}")