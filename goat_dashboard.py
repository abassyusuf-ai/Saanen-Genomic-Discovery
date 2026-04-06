import streamlit as st
import pandas as pd
import plotly.express as px
from scipy import stats

# --- PAGE CONFIG ---
st.set_page_config(page_title="Saanen Research Workflow", layout="wide")

# Initialize Session State to track which stage the user is in
if 'stage' not in st.session_state:
    st.session_state.stage = 1

def next_stage():
    st.session_state.stage = 2

def reset_stage():
    st.session_state.stage = 1

st.title("🧬 Saanen Goat Discovery Workflow")
st.markdown(f"**Current Progress: Stage {st.session_state.stage}**")

# ---------------------------------------------------------
# STAGE 1: GENOMIC QUALITY CONTROL
# ---------------------------------------------------------
if st.session_state.stage == 1:
    st.header("Stage 1: Genomic Population Analysis")
    st.info("Upload your 40GB extraction results to view the cluster of 298 goats.")
    
    genomic_file = st.file_uploader("📥 Upload genomic_stats.csv", type=['csv'])
    
    if genomic_file:
        df_gen = pd.read_csv(genomic_file)
        df_gen.columns = df_gen.columns.str.strip()
        df_gen['Het_Rate'] = df_gen['nHet'] / (df_gen['nHet'] + df_gen['nHomAlt'])

        # 1. The Main Population Cluster (The 298 Goats)
        st.subheader("Population Genomic Cluster (N=298)")
        fig_cluster = px.scatter(df_gen, x="nHomAlt", y="nHet", size="Depth",
                                 hover_name="Sample", template="plotly_dark",
                                 title="Genomic Distribution: Diversity vs. Stability",
                                 color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig_cluster, use_container_width=True)

        # 2. Additional Graphical Representations (Phase 1 Stats)
        c1, c2 = st.columns(2)
        with c1:
            fig_titv = px.histogram(df_gen, x="TiTv", title="Ti/Tv Ratio Distribution", 
                                   nbins=30, template="plotly_dark")
            st.plotly_chart(fig_titv, use_container_width=True)
        with c2:
            fig_het = px.violin(df_gen, y="Het_Rate", box=True, points="all",
                               title="Heterozygosity Rate (Diversity Index)", template="plotly_dark")
            st.plotly_chart(fig_het, use_container_width=True)

        # BUTTON TO MOVE TO STAGE 2
        st.markdown("---")
        st.button("Proceed to Stage 2: Phenotype Association ➡️", on_click=next_stage)

# ---------------------------------------------------------
# STAGE 2: PHENOTYPE ASSOCIATION
# ---------------------------------------------------------
if st.session_state.stage == 2:
    st.header("Stage 2: Milk Quality Association")
    
    # We need the user to re-upload or we use a persistent cache
    # For simplicity in this script, we ask for both to perform the merge
    st.warning("Please upload both files to finalize the association.")
    
    c1, c2 = st.columns(2)
    with c1:
        gen_file = st.file_uploader("📂 Re-confirm genomic_stats.csv", type=['csv'])
    with c2:
        pheno_file = st.file_uploader("📥 Upload milk_phenotypes.csv", type=['csv'])

    if gen_file and pheno_file:
        df_gen = pd.read_csv(gen_file)
        df_pheno = pd.read_csv(pheno_file)
        
        # Merge
        merged_df = pd.merge(df_gen, df_pheno, on='Sample', how='inner')
        
        trait = st.selectbox("Select Milk Quality Trait:", [c for c in df_pheno.columns if c != 'Sample'])

        # 1. The Discovery Map (Colorized)
        st.subheader(f"Discovery Map: {trait} Correlation")
        fig_final = px.scatter(merged_df, x="nHomAlt", y="nHet", color=trait,
                              size="Depth", hover_name="Sample",
                              color_continuous_scale="Viridis", template="plotly_dark")
        st.plotly_chart(fig_final, use_container_width=True)

        # 2. Statistical Analysis
        r, p = stats.pearsonr(merged_df['nHomAlt'], merged_df[trait])
        st.metric("Pearson Correlation (r)", f"{r:.3f}")
        if p < 0.05:
            st.success("✅ Statistical Significance Achieved!")
        else:
            st.warning("⚠️ Trend detected, but higher sample count needed for p < 0.05.")

        st.button("⬅️ Back to Stage 1", on_click=reset_stage)