import streamlit as st
import pandas as pd
import plotly.express as px
from scipy import stats
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
st.markdown("#### Phase 2: High-Speed Genomic & Phenotypic Integration")

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔬 Selection Criteria")
depth_min = st.sidebar.slider("Min Sequencing Depth", 0, 1000000, 50000)
het_filter = st.sidebar.slider("Heterozygosity Rate Filter", 0.0, 1.0, (0.0, 0.70))

# --- DUAL CSV INGESTION ---
col_u1, col_u2 = st.columns(2)
with col_u1:
    genomic_file = st.file_uploader("📥 STEP 1: Upload genomic_stats.csv", type=['csv'])
with col_u2:
    pheno_file = st.file_uploader("📥 STEP 2: Upload milk_phenotypes.csv", type=['csv'])

if genomic_file and pheno_file:
    try:
        # 1. Load Data
        df_gen = pd.read_csv(genomic_file)
        df_pheno = pd.read_csv(pheno_file)

        # 2. Clean and Match Sample IDs
        df_gen.columns = df_gen.columns.str.strip()
        df_pheno.columns = df_pheno.columns.str.strip()
        
        df_gen['Sample'] = df_gen['Sample'].astype(str)
        df_pheno['Sample'] = df_pheno['Sample'].astype(str)

        # 3. Inner Merge (Removes any goats missing DNA or Milk data)
        merged_df = pd.merge(df_gen, df_pheno, on='Sample', how='inner')
        
        # 4. Feature Engineering
        merged_df['Het_Rate'] = merged_df['nHet'] / (merged_df['nHet'] + merged_df['nHomAlt'])
        
        # 5. Dropdown for Milk Trait
        traits = [c for c in df_pheno.columns if c != 'Sample']
        selected_trait = st.selectbox("Select Milk Trait for Discovery Map:", traits)

        # 6. Apply Filters
        df_final = merged_df[
            (merged_df['Depth'] >= depth_min) & 
            (merged_df['Het_Rate'].between(het_filter[0], het_filter[1]))
        ].copy()

        # --- DASHBOARD METRICS ---
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Samples Synced", len(df_final))
        m2.metric("Avg Ti/Tv", f"{df_final['TiTv'].mean():.2f}")
        m3.metric("Avg Het_Rate", f"{df_final['Het_Rate'].mean():.3f}")
        m4.metric(f"Mean {selected_trait}", f"{df_final[selected_trait].mean():.2f}")

        # --- VISUALIZATION TABS ---
        t1, t2, t3 = st.tabs(["🎯 Discovery Map", "📊 Statistical Proof", "🌡️ Elite Founder List"])

        with t1:
            st.subheader(f"Correlation: Genomic Stability vs. {selected_trait}")
            # X-axis is nHomAlt (Fixed variants), Y-axis is nHet (Diversity)
            fig = px.scatter(df_final, x="nHomAlt", y="nHet", 
                             color=selected_trait, size="Depth",
                             hover_name="Sample", color_continuous_scale="Viridis",
                             template="plotly_dark",
                             labels={"nHomAlt": "Homozygous Variants (Genomic Stability)", 
                                     "nHet": "Heterozygous Variants (Diversity)"})
            st.plotly_chart(fig, use_container_width=True)

        with t2:
            st.subheader("Scientific Significance Test")
            # Calculate Pearson Correlation
            r, p = stats.pearsonr(df_final['nHomAlt'], df_final[selected_trait])
            
            st.write(f"Testing the relationship between **Genomic Stability (nHomAlt)** and **{selected_trait}**:")
            c1, c2 = st.columns(2)
            c1.metric("Pearson Correlation (r)", f"{r:.3f}")
            c2.metric("P-Value", f"{p:.4f}")
            
            if p < 0.05:
                st.success(f"✅ SUCCESS: There is a statistically significant link between these markers and {selected_trait}!")
            else:
                st.warning("⚠️ No significant linear trend detected. Try filtering by Depth to remove noise.")

        with t3:
            st.subheader("Top Goats for Selective Breeding")
            # Sort by the selected milk trait to find the best producers
            st.dataframe(df_final.sort_values(selected_trait, ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Integration Error: {e}")
else:
    st.info("Please upload both CSV files to begin the discovery process.")