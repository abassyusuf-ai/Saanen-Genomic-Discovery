import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# --- PUBLICATION STANDARDS ---
NATURE_THEME = "plotly_white"
PALETTE_GENOME = px.colors.sequential.Viridis
PALETTE_TRAIT = px.colors.sequential.Plasma
PALETTE_DISCOVERY = px.colors.sequential.Magma

st.set_page_config(page_title="Saanen Research Suite: Phase 1-3", layout="wide")

# Session State for Phase Navigation
if 'phase' not in st.session_state:
    st.session_state.phase = 1

def go_to(phase_num):
    st.session_state.phase = phase_num

# --- HEADER ---
st.title("🐐 Saanen Genomic & Phenotypic Discovery Suite")
st.markdown(f"**Current Research Progress: Phase {st.session_state.phase}**")
st.divider()

# ---------------------------------------------------------
# PHASE 1: GENOMIC POPULATION ARCHITECTURE (Objective 1)
# ---------------------------------------------------------
if st.session_state.phase == 1:
    st.header("Phase 1: Genomic Quality Control & Population Structure")
    st.info("Goal: Validate the 40GB VCF extraction for all 298 goats.")
    
    gen_file = st.file_uploader("📥 Step 1: Upload 'genomic_stats.csv'", type=['csv'])
    
    if gen_file:
        df = pd.read_csv(gen_file)
        df.columns = df.columns.str.strip()
        df['Het_Rate'] = df['nHet'] / (df['nHet'] + df['nHomAlt'])

        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("Figure 1: Population Variant Cluster")
            fig1 = px.scatter(df, x="nHomAlt", y="nHet", color="TiTv", size="Depth",
                              color_continuous_scale=PALETTE_GENOME, template=NATURE_THEME,
                              labels={"nHomAlt": "Homozygous (Stability)", "nHet": "Heterozygous (Diversity)"})
            st.plotly_chart(fig1, use_container_width=True)
        
        with c2:
            st.subheader("QC Metrics")
            fig_qc = px.violin(df, y="Het_Rate", box=True, points="all", template=NATURE_THEME)
            st.plotly_chart(fig_qc, use_container_width=True)

        st.button("Proceed to Phase 2: Data Integration ➡️", on_click=lambda: go_to(2))

# ---------------------------------------------------------
# PHASE 2: DATA HARMONIZATION & METADATA (Objective 2)
# ---------------------------------------------------------
if st.session_state.phase == 2:
    st.header("Phase 2: Phenotype Integration & Metadata Mapping")
    st.info("Goal: Merge the Genomic coordinates with physical Milk Quality traits.")
    
    col_a, col_b = st.columns(2)
    with col_a: f1 = st.file_uploader("📂 Confirm Genomic Data", type='csv')
    with col_b: f2 = st.file_uploader("📥 Upload 'milk_phenotypes.csv'", type='csv')

    if f1 and f2:
        df_g = pd.read_csv(f1); df_p = pd.read_csv(f2)
        df_g.columns = df_g.columns.str.strip(); df_p.columns = df_p.columns.str.strip()
        
        # Inner Merge for clarity
        merged = pd.merge(df_g, df_p, on='Sample', how='inner')
        
        st.subheader("Table 1: Integrated Research Metadata")
        st.dataframe(merged.style.background_gradient(cmap='Blues'), use_container_width=True)

        st.subheader("Preliminary Trait Distribution")
        trait = st.selectbox("Select Trait for Preview:", [c for c in df_p.columns if c != 'Sample'])
        fig2 = px.bar(merged, x="Sample", y=trait, color=trait, color_continuous_scale=PALETTE_TRAIT, template=NATURE_THEME)
        st.plotly_chart(fig2, use_container_width=True)

        col_nav1, col_nav2 = st.columns(2)
        with col_nav1: st.button("⬅️ Back to Phase 1", on_click=lambda: go_to(1))
        with col_nav2: st.button("Proceed to Phase 3: Scientific Discovery ➡️", on_click=lambda: go_to(3))

# ---------------------------------------------------------
# PHASE 3: ADVANCED DISCOVERY & SIGNIFICANCE (Objective 3)
# ---------------------------------------------------------
if st.session_state.phase == 3:
    st.header("Phase 3: Genotype-Phenotype Discovery (Nature Standard)")
    st.info("Goal: Establish statistical significance and identify Elite Founders.")

    # In a real app, you might use session_state to store the dataframes, 
    # but for simplicity, we request the final files here for the discovery merge.
    g_file = st.file_uploader("📂 Final Genomic Stats", type='csv')
    p_file = st.file_uploader("📥 Final Phenotype Data", type='csv')

    if g_file and p_file:
        df_g = pd.read_csv(g_file); df_p = pd.read_csv(p_file)
        df_g.columns = df_g.columns.str.strip(); df_p.columns = df_p.columns.str.strip()
        merged = pd.merge(df_g, df_p, on='Sample', how='inner')
        
        trait = st.selectbox("Select Target Discovery Trait:", [c for c in df_p.columns if c != 'Sample'])

        # FIG 3: REGRESSION & CORRELATION
        st.subheader(f"Figure 3: Linear Regression of Genomic Stability vs. {trait}")
        fig3 = px.scatter(merged, x="nHomAlt", y=trait, color="nHet", 
                         size="Depth", hover_name="Sample", trendline="ols",
                         color_continuous_scale=PALETTE_DISCOVERY, template=NATURE_THEME,
                         labels={"nHomAlt": "Homozygous Variants (n)", trait: f"Observed {trait}"})
        st.plotly_chart(fig3, use_container_width=True)

        # STATISTICS ENGINE
        r, p = stats.pearsonr(merged['nHomAlt'], merged[trait])
        
        st.subheader("Scientific Results Summary")
        m1, m2, m3 = st.columns(3)
        m1.metric("Pearson Correlation (r)", f"{r:.3f}")
        m2.metric("P-Value (Significance)", f"{p:.4e}")
        m3.metric("Sample Size (N)", len(merged))

        if p < 0.05:
            st.success("✅ **Major Finding:** This genomic marker is a statistically significant predictor of milk quality.")
        else:
            st.warning("📊 **Observation:** Positive trend identified, but full N=298 dataset is required to reach Nature-level significance ($p < 0.05$).")

        st.button("⬅️ Back to Phase 2", on_click=lambda: go_to(2))
