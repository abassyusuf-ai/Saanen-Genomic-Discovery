import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import numpy as np

# --- PUBLICATION STANDARDS (Nature Formatting) ---
NATURE_THEME = "plotly_white"
PALETTE_GENOME = px.colors.sequential.Viridis
PALETTE_TRAIT = px.colors.sequential.Plasma
PALETTE_DISCOVERY = px.colors.sequential.Magma

st.set_page_config(page_title="Saanen Research Suite", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004d40; color: white; }
    .stMetric { border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; background-color: #fafafa; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'phase' not in st.session_state:
    st.session_state.phase = 1

def go_to(phase_num):
    st.session_state.phase = phase_num

# --- SIDEBAR ---
st.sidebar.title("🔬 Research Objectives")
st.sidebar.info(f"Currently in: Phase {st.session_state.phase}")
if st.sidebar.button("Reset to Phase 1"): go_to(1)

st.title("📊 Genomic Architecture of Milk Quality: Saanen Herd Analysis")
st.caption("Standardized Scientific Workflow for 298 Saanen Dairy Goats")
st.divider()

# ---------------------------------------------------------
# PHASE 1: GENOMIC QUALITY (Objective 1)
# ---------------------------------------------------------
if st.session_state.phase == 1:
    st.header("Phase 1: Population Genomic Structure")
    gen_file = st.file_uploader("📥 Upload 'genomic_stats.csv'", type=['csv'])
    
    if gen_file:
        df = pd.read_csv(gen_file)
        df.columns = df.columns.str.strip()
        df['Het_Rate'] = df['nHet'] / (df['nHet'] + df['nHomAlt'])

        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.subheader("Figure 1a: Population Genomic Cluster")
            fig1a = px.scatter(df, x="nHomAlt", y="nHet", color="TiTv", size="Depth",
                               color_continuous_scale=PALETTE_GENOME, template=NATURE_THEME)
            st.plotly_chart(fig1a, use_container_width=True)
        
        with col_b:
            st.subheader("Figure 1b: Diversity Index")
            fig1b = px.violin(df, y="Het_Rate", box=True, points="all", template=NATURE_THEME)
            st.plotly_chart(fig1b, use_container_width=True)

        st.success("✅ Data Validated.")
        st.button("Proceed to Phase 2 ➡️", on_click=lambda: go_to(2))

# ---------------------------------------------------------
# PHASE 2: PHENOTYPE INTEGRATION (Objective 2)
# ---------------------------------------------------------
if st.session_state.phase == 2:
    st.header("Phase 2: Phenotype Integration")
    c1, c2 = st.columns(2)
    with c1: f_gen = st.file_uploader("📂 Confirm Genomic Stats", type='csv', key="g2")
    with c2: f_pheno = st.file_uploader("📥 Upload 'milk_phenotypes.csv'", type='csv')

    if f_gen and f_pheno:
        df_g = pd.read_csv(f_gen); df_p = pd.read_csv(f_pheno)
        merged = pd.merge(df_g, df_p, on='Sample', how='inner')
        st.subheader("Table 1: Integrated Research Dataset")
        st.dataframe(merged.style.background_gradient(cmap='YlGnBu'), use_container_width=True)

        trait_prev = st.selectbox("Select Trait for Preview:", [c for c in df_p.columns if c != 'Sample'])
        fig2 = px.bar(merged, x="Sample", y=trait_prev, color=trait_prev, color_continuous_scale=PALETTE_TRAIT)
        st.plotly_chart(fig2, use_container_width=True)
        st.button("Proceed to Phase 3 ➡️", on_click=lambda: go_to(3))

# ---------------------------------------------------------
# PHASE 3: SCIENTIFIC DISCOVERY (Objective 3)
# ---------------------------------------------------------
if st.session_state.phase == 3:
    st.header("Phase 3: Genotype-Phenotype Association")
    g_file = st.file_uploader("📂 Final Genomic Data", type='csv', key="g3")
    p_file = st.file_uploader("📥 Final Phenotype Data", type='csv', key="p3")

    if g_file and p_file:
        df_g = pd.read_csv(g_file); df_p = pd.read_csv(p_file)
        df = pd.merge(df_g, df_p, on='Sample', how='inner')
        trait = st.selectbox("Select Discovery Target:", [c for c in df_p.columns if c != 'Sample'])

        # --- MANUAL REGRESSION (No statsmodels needed) ---
        slope, intercept, r_val, p_val, std_err = stats.linregress(df['nHomAlt'], df[trait])
        x_range = np.linspace(df['nHomAlt'].min(), df['nHomAlt'].max(), 100)
        y_range = slope * x_range + intercept

        fig3 = px.scatter(df, x="nHomAlt", y=trait, color="nHet", size="Depth",
                         color_continuous_scale=PALETTE_DISCOVERY, template=NATURE_THEME)
        
        # Add the trendline manually as a red line
        fig3.add_trace(go.Scatter(x=x_range, y=y_range, mode='lines', name='Regression Line', line=dict(color='red', width=3)))
        
        st.subheader(f"Figure 3: Linear Regression - Genomic Stability vs. {trait}")
        st.plotly_chart(fig3, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Pearson Correlation (r)", f"{r_val:.3f}")
        c2.metric("Significance (P-Value)", f"{p_val:.4e}")
        c3.metric("Population Size (N)", len(df))

        if p_val < 0.05:
            st.success("✅ **Finding:** This association is statistically significant.")
        else:
            st.warning("📊 **Finding:** Positive trend observed. More samples needed for significance.")

        st.subheader("Elite Selection: Top Producers")
        st.dataframe(df.sort_values(trait, ascending=False).head(10), use_container_width=True)