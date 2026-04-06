import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Saanen Genomic Discovery Suite", layout="wide")

# --- RESEARCH GRADE UI STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { 
        background-color: #161b22; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧬 Saanen Lineage & Milk-Marker Discovery")
st.markdown("#### Phase 2: Integrated CSV Phenotype-Genotype Analysis")

# --- SIDEBAR: DISCOVERY FILTERS ---
st.sidebar.header("🔬 Selection Criteria")
depth_min = st.sidebar.slider("Min Sequencing Depth", 0, 1000000, 100000)
het_range = st.sidebar.slider("Heterozygosity Rate Filter", 0.0, 1.0, (0.0, 0.60))

# --- DUAL CSV INGESTION ---
col_u1, col_u2 = st.columns(2)
with col_u1:
    genomic_file = st.file_uploader("📥 STEP 1: Upload genomic_stats.csv", type=['csv'])
with col_u2:
    pheno_file = st.file_uploader("📥 STEP 2: Upload milk_quality.csv", type=['csv'])

if genomic_file is not None and pheno_file is not None:
    try:
        # 1. LOAD DATA
        df_genomic = pd.read_csv(genomic_file)
        df_pheno = pd.read_csv(pheno_file)

        # 2. DATA SANITIZATION
        # Clean hidden spaces in headers
        df_genomic.columns = df_genomic.columns.str.strip()
        df_pheno.columns = df_pheno.columns.str.strip()

        # 3. AUTO-DETECT ID COLUMN IN MILK FILE
        id_candidates = ['Sample', 'ID', 'SampleID', 'Individual', 'Name', 'goat_id']
        found_id = next((c for c in df_pheno.columns if c in id_candidates or c.lower() in [i.lower() for i in id_candidates]), df_pheno.columns[0])
        df_pheno = df_pheno.rename(columns={found_id: 'Sample'})

        # 4. DATA MERGING
        # Ensure 'Sample' is string-type in both to prevent merge mismatch
        df_genomic['Sample'] = df_genomic['Sample'].astype(str)
        df_pheno['Sample'] = df_pheno['Sample'].astype(str)
        
        # Perform Left Join
        final_df = pd.merge(df_genomic, df_pheno, on='Sample', how='left')
        st.success(f"✅ Successfully linked Genomic Data with Phenotypes using column: **{found_id}**")

        # 5. GENOMIC CALCULATIONS
        final_df['Het_Rate'] = final_df['nHet'] / (final_df['nHet'] + final_df['nHomAlt'])
        
        # Identify numeric traits for colorization
        trait_options = [c for c in df_pheno.columns if c != 'Sample']
        color_target = st.selectbox("Colorize Discovery Map by Phenotype:", trait_options)

        # 6. APPLY FILTERS
        df_filtered = final_df[
            (final_df['Depth'] >= depth_min) & 
            (final_df['Het_Rate'].between(het_range[0], het_range[1]))
        ].dropna(subset=['nHet', 'nHomAlt'])

        # --- TOP LEVEL METRIC CARDS ---
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Samples Mapped", len(df_filtered))
        m2.metric("Avg Ti/Tv", f"{df_filtered['TiTv'].mean():.2f}")
        m3.metric("Avg Het_Rate", f"{df_filtered['Het_Rate'].mean():.3f}")
        m4.metric("Potential Founders", len(df_filtered[df_filtered['nHomAlt'] > 5000000]))

        # --- DISCOVERY TABS ---
        t1, t2, t3, t4 = st.tabs(["🎯 Discovery Map", "📊 Pop. Distribution", "🧬 Variant Density", "🌡️ Lead-List"])

        with t1:
            st.subheader("Selection Pressure & Phenotype Correlation")
            fig1 = px.scatter(df_filtered, x="nHet", y="nHomAlt", color=color_target, 
                             size="Depth", hover_name="Sample", 
                             color_continuous_scale="Viridis", 
                             labels={"nHet": "Heterozygous Count", "nHomAlt": "Homozygous Alt Count"},
                             template="plotly_dark")
            st.plotly_chart(fig1, use_container_width=True)

        with t2:
            st.subheader("Nature-Style Heterozygosity (Diversity Check)")
            fig2 = px.violin(df_filtered, y="Het_Rate", box=True, points="all", 
                            hover_name="Sample", color_discrete_sequence=["#BB5566"],
                            template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

        with t3:
            st.subheader("Simulated Chromosomal Variant Density (2n=60)")
            # Simulated data representing your Saanen genome density hotspots
            chrom_data = pd.DataFrame({'CHR': [f"Chr{i}" for i in range(1, 31)], 
                                     'Density': np.random.uniform(0.5, 3.0, 30)})
            st.plotly_chart(px.bar(chrom_data, x='CHR', y='Density', color='Density', 
                                  color_continuous_scale='Reds', template='plotly_dark'), use_container_width=True)

        with t4:
            st.subheader("Candidate Lead-List (Ranked by Genetic Stabilization)")
            # Showing the full merged table for ranking
            st.dataframe(df_filtered.sort_values('nHomAlt', ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Dashboard System Error: {e}")
        st.info("Check if your CSV headers match the required genomic stats (Sample, nHet, nHomAlt, TiTv, Depth).")

else:
    st.warning("🚀 Please upload both **genomic_stats.csv** and **milk_quality.csv** to begin analysis.")