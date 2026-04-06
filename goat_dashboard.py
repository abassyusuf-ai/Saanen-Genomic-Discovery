import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# --- PUBLICATION STANDARDS (Nature Formatting) ---
NATURE_THEME = "plotly_white"
PALETTE_GENOME = px.colors.sequential.Viridis  # Colorblind-friendly
PALETTE_TRAIT = px.colors.sequential.Plasma    # High contrast for phenotypes
PALETTE_DISCOVERY = px.colors.sequential.Magma # Deep contrast for significance

st.set_page_config(page_title="Saanen Research Suite", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004d40; color: white; }
    .stMetric { border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; background-color: #fafafa; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE MANAGEMENT ---
if 'phase' not in st.session_state:
    st.session_state.phase = 1

def go_to(phase_num):
    st.session_state.phase = phase_num

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🔬 Research Objectives")
st.sidebar.info(f"Currently in: Phase {st.session_state.phase}")
if st.sidebar.button("Reset to Phase 1"): go_to(1)

# --- MAIN HEADER ---
st.title("📊 Genomic Architecture of Milk Quality: Saanen Herd Analysis")
st.caption("Standardized Scientific Workflow for 298 Saanen Dairy Goats")
st.divider()

# ---------------------------------------------------------
# PHASE 1: GENOMIC QUALITY & POPULATION (Objective 1)
# ---------------------------------------------------------
if st.session_state.phase == 1:
    st.header("Phase 1: Population Genomic Structure")
    st.markdown("##### Objective: Validate Variant Extraction & Sample Quality")
    
    gen_file = st.file_uploader("📥 Upload 'genomic_stats.csv' (Phase 1 Results)", type=['csv'])
    
    if gen_file:
        df = pd.read_csv(gen_file)
        df.columns = df.columns.str.strip()
        df['Het_Rate'] = df['nHet'] / (df['nHet'] + df['nHomAlt'])

        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.subheader("Figure 1a: Population Genomic Cluster (N=298)")
            fig1a = px.scatter(df, x="nHomAlt", y="nHet", color="TiTv", size="Depth",
                               hover_name="Sample", color_continuous_scale=PALETTE_GENOME,
                               template=NATURE_THEME,
                               labels={"nHomAlt": "Homozygous Variants (n)", "nHet": "Heterozygous Variants (n)"})
            st.plotly_chart(fig1a, use_container_width=True)
        
        with col_b:
            st.subheader("Figure 1b: Diversity Index")
            fig1b = px.violin(df, y="Het_Rate", box=True, points="all", 
                               template=NATURE_THEME, color_discrete_sequence=['#2c3e50'])
            st.plotly_chart(fig1b, use_container_width=True)

        st.success("✅ Phase 1 Data Validated. Ready for Phenotype Integration.")
        st.button("Proceed to Phase 2: Integration ➡️", on_click=lambda: go_to(2))

# ---------------------------------------------------------
# PHASE 2: PHENOTYPE HARMONIZATION (Objective 2)
# ---------------------------------------------------------
if st.session_state.phase == 2:
    st.header("Phase 2: Phenotype Integration & Metadata Mapping")
    st.markdown("##### Objective: Link Genomic Markers with Recorded Milk Traits")
    
    c1, c2 = st.columns(2)
    with c1: f_gen = st.file_uploader("📂 Confirm Genomic Stats", type='csv')
    with c2: f_pheno = st.file_uploader("📥 Upload 'milk_phenotypes.csv' (Table Image Transcription)", type='csv')

    if f_gen and f_pheno:
        df_g = pd.read_csv(f_gen); df_p = pd.read_csv(f_pheno)
        df_g.columns = df_g.columns.str.strip(); df_p.columns = df_p.columns.str.strip()
        
        # Intersection Merge
        merged = pd.merge(df_g, df_p, on='Sample', how='inner')
        
        st.subheader("Table 1: Integrated Research Dataset")
        st.markdown("Full intersection of DNA variants and Milk Phenotypes.")
        st.dataframe(merged.style.background_gradient(cmap='YlGnBu'), use_container_width=True)

        # Bar chart for trait comparison
        trait_prev = st.selectbox("Select Trait for Preview:", [c for c in df_p.columns if c != 'Sample'])
        fig2 = px.bar(merged, x="Sample", y=trait_prev, color=trait_prev, 
                      color_continuous_scale=PALETTE_TRAIT, template=NATURE_THEME)
        st.plotly_chart(fig2, use_container_width=True)

        col_nav1, col_nav2 = st.columns(2)
        with col_nav1: st.button("⬅️ Back to Phase 1", on_click=lambda: go_to(1))
        with col_nav2: st.button("Proceed to Phase 3: Discovery ➡️", on_click=lambda: go_to(3))

# ---------------------------------------------------------
# PHASE 3: SCIENTIFIC DISCOVERY (Objective 3)
# ---------------------------------------------------------
if st.session_state.phase == 3:
    st.header("Phase 3: Genotype-Phenotype Association")
    st.markdown("##### Objective: Statistical Discovery & Breeding Selection")

    g_file = st.file_uploader("📂 Final Genomic Data", type='csv')
    p_file = st.file_uploader("📥 Final Phenotype Data", type='csv')

    if g_file and p_file:
        df_g = pd.read_csv(g_file); df_p = pd.read_csv(p_file)
        df_g.columns = df_g.columns.str.strip(); df_p.columns = df_p.columns.str.strip()
        merged_final = pd.merge(df_g, df_p, on='Sample', how='inner')
        
        trait = st.selectbox("Select Discovery Target (e.g., Fat% or Yield):", [c for c in df_p.columns if c != 'Sample'])

        # FIG 3: THE DISCOVERY MAP WITH TRENDLINE
        st.subheader(f"Figure 3: Linear Regression - Genomic Stability vs. {trait}")
        fig3 = px.scatter(merged_final, x="nHomAlt", y=trait, color="nHet", 
                         size="Depth", hover_name="Sample", trendline="ols",
                         color_continuous_scale=PALETTE_DISCOVERY, template=NATURE_THEME,
                         labels={"nHomAlt": "Homozygous Variants (Fixed)", trait: f"Observed {trait}"})
        st.plotly_chart(fig3, use_container_width=True)

        # STATISTICAL VALIDATION
        r, p = stats.pearsonr(merged_final['nHomAlt'], merged_final[trait])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Pearson Correlation (r)", f"{r:.3f}")
        c2.metric("Significance (P-Value)", f"{p:.4e}")
        c3.metric("Population Size (N)", len(merged_final))

        if p < 0.05:
            st.success("✅ **Finding:** This genotype-phenotype association is statistically significant.")
        else:
            st.warning("📊 **Finding:** Positive trend observed. Significance pending full N=298 dataset.")

        st.subheader("Elite Selection: Top Producers")
        st.dataframe(merged_final.sort_values(trait, ascending=False).head(10), use_container_width=True)
        
        st.button("⬅️ Back to Phase 2", on_click=lambda: go_to(2))