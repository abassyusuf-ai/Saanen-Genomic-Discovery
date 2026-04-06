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
PALETTE_MERIT = "RdYlGn" # Red-Yellow-Green for Selection

st.set_page_config(page_title="Saanen Research Suite", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004d40; color: white; font-weight: bold; }
    .stMetric { border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; background-color: #fafafa; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE MANAGEMENT ---
if 'phase' not in st.session_state:
    st.session_state.phase = 1

def go_to(phase_num):
    st.session_state.phase = phase_num

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Research Objectives")
st.sidebar.info(f"Active Phase: {st.session_state.phase}")
if st.sidebar.button("Phase 1: Population"): go_to(1)
if st.sidebar.button("Phase 2: Integration"): go_to(2)
if st.sidebar.button("Phase 3: Discovery"): go_to(3)
if st.sidebar.button("Phase 4: Selection"): go_to(4)
st.sidebar.divider()
if st.sidebar.button("Reset All"): st.session_state.clear(); st.rerun()

# --- MAIN HEADER ---
st.title("Genomic Architecture of Milk Quality: Saanen Herd Analysis")
st.caption("Standardized Scientific Workflow for 298 Saanen Dairy Goats | Objectives 1-4")
st.divider()

# ---------------------------------------------------------
# PHASE 1: GENOMIC QUALITY (Objective 1)
# ---------------------------------------------------------
if st.session_state.phase == 1:
    st.header("Phase 1: Population Genomic Structure")
    gen_file = st.file_uploader("📥 Upload 'genomic_stats.csv'", type=['csv'], key="p1_upload")
    
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

        st.success("Objective 1 Validated. Ready for Integration.")
        st.button("Proceed to Phase 2 ➡️", on_click=lambda: go_to(2))

# ---------------------------------------------------------
# PHASE 2: PHENOTYPE INTEGRATION (Objective 2)
# ---------------------------------------------------------
elif st.session_state.phase == 2:
    st.header("Phase 2: Phenotype Integration")
    c1, c2 = st.columns(2)
    with c1: f_gen = st.file_uploader("Confirm Genomic Stats", type='csv', key="g2_upload")
    with c2: f_pheno = st.file_uploader("Upload 'milk_phenotypes.csv'", type='csv', key="p2_upload")

    if f_gen and f_pheno:
        df_g = pd.read_csv(f_gen); df_p = pd.read_csv(f_pheno)
        df_g.columns = df_g.columns.str.strip(); df_p.columns = df_p.columns.str.strip()
        df_g['Sample'] = df_g['Sample'].astype(str).str.strip()
        df_p['Sample'] = df_p['Sample'].astype(str).str.strip()
        
        merged = pd.merge(df_g, df_p, on='Sample', how='inner')
        st.subheader("Table 1: Integrated Research Dataset")
        st.dataframe(merged.style.background_gradient(cmap='YlGnBu'), use_container_width=True)

        trait_prev = st.selectbox("Select Trait for Bar Representation:", [c for c in df_p.columns if c != 'Sample'])
        fig2 = px.bar(merged, x="Sample", y=trait_prev, color=trait_prev, 
                     color_continuous_scale=PALETTE_TRAIT, template=NATURE_THEME)
        st.plotly_chart(fig2, use_container_width=True)
        st.button("Proceed to Phase 3 ", on_click=lambda: go_to(3))

# ---------------------------------------------------------
# PHASE 3: SCIENTIFIC DISCOVERY (Objective 3)
# ---------------------------------------------------------
elif st.session_state.phase == 3:
    st.header("Phase 3: Genotype-Phenotype Association")
    g_file = st.file_uploader("Final Genomic Data", type='csv', key="g3_upload")
    p_file = st.file_uploader("Final Phenotype Data", type='csv', key="p3_upload")

    if g_file and p_file:
        df_g = pd.read_csv(g_file); df_p = pd.read_csv(p_file)
        df_g.columns = df_g.columns.str.strip(); df_p.columns = df_p.columns.str.strip()
        df = pd.merge(df_g, df_p, on='Sample', how='inner')
        
        trait = st.selectbox("Select Discovery Target:", [c for c in df_p.columns if c != 'Sample'])

        # Manual Linear Regression
        slope, intercept, r_val, p_val, std_err = stats.linregress(df['nHomAlt'], df[trait])
        x_range = np.linspace(df['nHomAlt'].min(), df['nHomAlt'].max(), 100)
        y_range = slope * x_range + intercept

        fig3 = px.scatter(df, x="nHomAlt", y=trait, color="nHet", size="Depth",
                         color_continuous_scale=PALETTE_DISCOVERY, template=NATURE_THEME)
        fig3.add_trace(go.Scatter(x=x_range, y=y_range, mode='lines', name='OLS Line', line=dict(color='red', width=3)))
        st.plotly_chart(fig3, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Correlation (r)", f"{r_val:.3f}")
        c2.metric("Significance (P)", f"{p_val:.4e}")
        c3.metric("Samples (N)", len(df))

        st.success(f"Objective 3: {trait} Association Analyzed.")
        st.button("Proceed to Phase 4: Selection ➡️", on_click=lambda: go_to(4))

# ---------------------------------------------------------
# PHASE 4: ELITE BREEDING SELECTION (Objective 4)
# ---------------------------------------------------------
elif st.session_state.phase == 4:
    st.header("Phase 4: Elite Selection & Genomic Prediction")
    st.markdown("##### Objective: Identify High-Merit Individuals for Breeding Programs")
    
    g_f = st.file_uploader("Final Genomic Data", type='csv', key="g4_upload")
    p_f = st.file_uploader("Final Phenotype Data", type='csv', key="p4_upload")

    if g_f and p_f:
        df_g = pd.read_csv(g_f); df_p = pd.read_csv(p_f)
        df_g.columns = df_g.columns.str.strip(); df_p.columns = df_p.columns.str.strip()
        df = pd.merge(df_g, df_p, on='Sample', how='inner')
        trait = st.selectbox("Select Breeding Objective (Trait):", [c for c in df_p.columns if c != 'Sample'])

        # CALCULATE GENETIC MERIT SCORE
        df['Merit_Score'] = (df[trait] / df[trait].max()) - (df['nHomAlt'] / df['nHomAlt'].max())
        
        # --- THE FIX ---
        # Normalize size to be strictly positive (Merit Score - min value + 0.1 offset)
        df['Display_Size'] = df['Merit_Score'] - df['Merit_Score'].min() + 0.1
        
        col_x, col_y = st.columns([2, 1])
        with col_x:
            st.subheader("Figure 4: Selection Pressure Map")
            # We use 'Display_Size' for visual marker size to prevent the ValueError
            fig4 = px.scatter(df, x="nHomAlt", y=trait, size="Display_Size", color="Merit_Score",
                              hover_name="Sample", color_continuous_scale=PALETTE_MERIT, template=NATURE_THEME)
            st.plotly_chart(fig4, use_container_width=True)
            st.info(" **Interpretation:** Larger, Green circles indicate superior breeding candidates.")

        with col_y:
            st.subheader("Elite Breeding Candidates")
            elites = df.sort_values("Merit_Score", ascending=False).head(5)
            for i, row in elites.iterrows():
                st.metric(f"Goat ID: {row['Sample']}", f"Merit: {row['Merit_Score']:.3f}", f"Rank {i+1}")

        st.divider()
        st.success(" **Objective 4 Complete:** Breeding selection generated.")
