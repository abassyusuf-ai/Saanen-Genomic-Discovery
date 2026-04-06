import streamlit as st
import pandas as pd
import plotly.express as px
from scipy import stats

# --- PAGE CONFIG ---
st.set_page_config(page_title="Saanen Integrated Research Suite", layout="wide")

st.title("🧬 Saanen Discovery: Phase 1 (Genomic) + Phase 2 (Milk) Integration")
st.markdown("---")

# --- DATA INGESTION ---
col_u1, col_u2 = st.columns(2)
with col_u1:
    st.subheader("Phase 1: DNA Variants")
    genomic_file = st.file_uploader("Upload genomic_stats.csv", type=['csv'])
with col_u2:
    st.subheader("Phase 2: Milk Quality")
    pheno_file = st.file_uploader("Upload milk_phenotypes.csv", type=['csv'])

if genomic_file and pheno_file:
    try:
        # Load and Sync
        df_gen = pd.read_csv(genomic_file).apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        df_pheno = pd.read_csv(pheno_file).apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        
        df_gen['Sample'] = df_gen['Sample'].astype(str)
        df_pheno['Sample'] = df_pheno['Sample'].astype(str)
        
        # Merge - This creates the connection between DNA and Milk
        merged_df = pd.merge(df_gen, df_pheno, on='Sample', how='inner')
        merged_df['Het_Rate'] = merged_df['nHet'] / (merged_df['nHet'] + merged_df['nHomAlt'])

        # --- RESEARCH TABS ---
        t1, t2, t3 = st.tabs(["🎯 Discovery Map (Integrated)", "📊 Population Distribution", "🏆 Elite Founder Analysis"])

        with t1:
            st.subheader("The Integrated Marker Map")
            trait = st.selectbox("Colorize by Milk Trait:", [c for c in df_pheno.columns if c != 'Sample'])
            
            # This replicates the 'phy.png' chart from Phase 2 using Phase 1 data
            fig1 = px.scatter(merged_df, x="nHomAlt", y="nHet", color=trait, 
                             size="Depth", hover_name="Sample", 
                             color_continuous_scale="Viridis", template="plotly_dark",
                             labels={"nHomAlt": "Homozygous (Stability)", "nHet": "Heterozygous (Diversity)"})
            st.plotly_chart(fig1, use_container_width=True)

        with t2:
            st.subheader("Genetic Diversity Spread")
            # This replicates the Phase 1 distribution charts
            fig2 = px.violin(merged_df, y="Het_Rate", box=True, points="all", template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

        with t3:
            st.subheader("Top Performers (The 'Elite' Group)")
            elite_count = st.slider("Select number of top goats to view:", 1, len(merged_df), 4)
            elite_df = merged_df.sort_values(trait, ascending=False).head(elite_count)
            
            st.dataframe(elite_df[['Sample', 'nHomAlt', 'nHet', trait, 'TiTv']], use_container_width=True)
            
            # Statistical Correlation
            r, p = stats.pearsonr(merged_df['nHomAlt'], merged_df[trait])
            st.write(f"**Research Note:** Correlation between DNA Stability and {trait} is **{r:.3f}**.")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
else:
    st.info("Upload both files to see the Phase 1 & Phase 2 integrated charts.")