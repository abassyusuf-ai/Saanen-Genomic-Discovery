import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Saanen Genomic Discovery Suite", layout="wide")

# --- UI STYLING ---
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
st.markdown("#### Phase 2: High-Speed CSV Integration")

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔬 Selection Criteria")
depth_min = st.sidebar.slider("Min Sequencing Depth", 0, 1000000, 100000)
het_range = st.sidebar.slider("Heterozygosity Rate Filter", 0.0, 1.0, (0.0, 0.60))

# --- DUAL CSV INGESTION ---
col_u1, col_u2 = st.columns(2)
with col_u1:
    genomic_file = st.file_uploader("📥 STEP 1: genomic_stats.csv", type=['csv'])
with col_u2:
    pheno_file = st.file_uploader("📥 STEP 2: milk_quality.csv", type=['csv'])

if genomic_file and pheno_file:
    try:
        # Load with 'on_bad_lines' to handle any remaining jagged rows from Line 23
        df_genomic = pd.read_csv(genomic_file, on_bad_lines='skip', engine='python')
        df_pheno = pd.read_csv(pheno_file, on_bad_lines='skip', engine='python')

        # Clean headers & force Sample IDs to strings for perfect matching
        df_genomic.columns = df_genomic.columns.str.strip()
        df_pheno.columns = df_pheno.columns.str.strip()
        
        # Auto-match the ID column in the milk file
        id_targets = ['Sample', 'ID', 'SampleID', 'Individual']
        found_id = next((c for c in df_pheno.columns if c in id_targets or c.lower() in [i.lower() for i in id_targets]), df_pheno.columns[0])
        df_pheno = df_pheno.rename(columns={found_id: 'Sample'})

        df_genomic['Sample'] = df_genomic['Sample'].astype(str)
        df_pheno['Sample'] = df_pheno['Sample'].astype(str)

        # Merge & Calculate Metrics
        final_df = pd.merge(df_genomic, df_pheno, on='Sample', how='left')
        final_df['Het_Rate'] = final_df['nHet'] / (final_df['nHet'] + final_df['nHomAlt'])
        
        # Select Phenotype for the Y-Axis/Color
        trait_options = [c for c in df_pheno.columns if c != 'Sample']
        color_target = st.selectbox("Colorize Discovery Map by:", trait_options)

        # Apply Filtering
        df_filtered = final_df[
            (final_df['Depth'] >= depth_min) & 
            (final_df['Het_Rate'].between(het_range[0], het_range[1]))
        ].dropna(subset=['nHet', 'nHomAlt'])

        # --- DASHBOARD ---
        m1, m2, m3 = st.columns(3)
        m1.metric("Samples Mapped", len(df_filtered))
        m2.metric("Avg Ti/Tv", f"{df_filtered['TiTv'].mean():.2f}")
        m3.metric("Avg Het_Rate", f"{df_filtered['Het_Rate'].mean():.3f}")

        t1, t2, t3 = st.tabs(["🎯 Discovery Map", "📊 Pop. Distribution", "🌡️ Lead-List"])

        with t1:
            st.subheader("Selection Pressure & Phenotype Correlation")
            fig1 = px.scatter(df_filtered, x="nHet", y="nHomAlt", color=color_target, 
                             size="Depth", hover_name="Sample", 
                             color_continuous_scale="Viridis", template="plotly_dark")
            st.plotly_chart(fig1, use_container_width=True)

        with t2:
            fig2 = px.violin(df_filtered, y="Het_Rate", box=True, points="all", template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

        with t3:
            st.dataframe(df_filtered.sort_values('nHomAlt', ascending=False))

    except Exception as e:
        st.error(f"⚠️ Dashboard Error: {e}")