import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# --- PUBLICATION THEME SETTINGS ---
# Nature journals prefer clean white backgrounds and high-contrast scales
SCIENTIFIC_TEMPLATE = "plotly_white" 
COLOR_DIVERSITY = px.colors.sequential.Viridis
COLOR_TRAIT = px.colors.sequential.Magma

st.set_page_config(page_title="Saanen Genomic Discovery: Nature Standards", layout="wide")

# Custom CSS for a professional "Paper-like" feel
st.markdown("""
    <style>
    .stMetric { border-left: 5px solid #004d40; background-color: #f8f9fa; padding: 10px; }
    h1, h2, h3 { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #202124; }
    </style>
    """, unsafe_allow_html=True)

if 'stage' not in st.session_state:
    st.session_state.stage = 1

st.title("📊 Genomic Architecture of Milk Quality in Saanen Goats")
st.caption("Standardized Visualization Suite for Scientific Publication")

# ---------------------------------------------------------
# STAGE 1: GENOMIC POPULATION STRUCTURE (Figure 1)
# ---------------------------------------------------------
if st.session_state.stage == 1:
    st.header("Stage 1: Genomic Quality & Population Structure")
    genomic_file = st.file_uploader("📥 Upload 'genomic_stats.csv' (n=298)", type=['csv'])
    
    if genomic_file:
        df = pd.read_csv(genomic_file)
        df.columns = df.columns.str.strip()
        df['Het_Rate'] = df['nHet'] / (df['nHet'] + df['nHomAlt'])

        col_a, col_b = st.columns([2, 1])

        with col_a:
            st.subheader("Figure 1a: Population Variant Cluster")
            fig1a = px.scatter(df, x="nHomAlt", y="nHet", color="TiTv",
                               size="Depth", hover_name="Sample", 
                               color_continuous_scale=COLOR_DIVERSITY,
                               labels={"nHomAlt": "Homozygous Variants (n)", "nHet": "Heterozygous Variants (n)"},
                               template=SCIENTIFIC_TEMPLATE)
            fig1a.update_layout(font_family="Arial", title_font_size=20)
            st.plotly_chart(fig1a, use_container_width=True)

        with col_b:
            st.subheader("Figure 1b: Ti/Tv Quality")
            fig1b = px.histogram(df, x="TiTv", nbins=20, 
                                 template=SCIENTIFIC_TEMPLATE, color_discrete_sequence=['#2c3e50'])
            st.plotly_chart(fig1b, use_container_width=True)
            
            st.subheader("Figure 1c: Heterozygosity")
            fig1c = px.violin(df, y="Het_Rate", box=True, points="all",
                               template=SCIENTIFIC_TEMPLATE, color_discrete_sequence=['#1a73e8'])
            st.plotly_chart(fig1c, use_container_width=True)

        st.divider()
        st.button("Proceed to Phenotype Association ➡️", on_click=lambda: st.session_state.update({"stage": 2}))

# ---------------------------------------------------------
# STAGE 2: PHENOTYPE ASSOCIATION (Figure 2 & Table 1)
# ---------------------------------------------------------
if st.session_state.stage == 2:
    st.header("Stage 2: Genotype-Phenotype Association")
    
    c1, c2 = st.columns(2)
    with c1: g_file = st.file_uploader("📂 Re-confirm Genomic Data", type=['csv'])
    with c2: p_file = st.file_uploader("📥 Upload Phenotype Data", type=['csv'])

    if g_file and p_file:
        df_g = pd.read_csv(g_file)
        df_p = pd.read_csv(p_file)
        df_g.columns = df_g.columns.str.strip()
        df_p.columns = df_p.columns.str.strip()
        
        # Merging (Handling missing values by showing intersected population)
        merged = pd.merge(df_g, df_p, on='Sample', how='inner')
        trait = st.selectbox("Select Trait for Analysis:", [c for c in df_p.columns if c != 'Sample'])

        # FIG 2A: The Discovery Map
        st.subheader(f"Figure 2a: Genomic Correlation with {trait}")
        fig2a = px.scatter(merged, x="nHomAlt", y="nHet", color=trait,
                           size="Depth", hover_name="Sample",
                           color_continuous_scale=COLOR_TRAIT, 
                           template=SCIENTIFIC_TEMPLATE,
                           labels={"nHomAlt": "Fixed Variants (n)", "nHet": "Diverse Variants (n)"})
        st.plotly_chart(fig2a, use_container_width=True)

        # FIG 2B: Rank Bar Chart
        st.subheader(f"Figure 2b: Top Performing Samples ({trait})")
        top10 = merged.sort_values(trait, ascending=False).head(10)
        fig2b = px.bar(top10, x="Sample", y=trait, color=trait,
                       color_continuous_scale="Agsunset", text_auto='.2f',
                       template=SCIENTIFIC_TEMPLATE)
        st.plotly_chart(fig2b, use_container_width=True)

        # --- THE MASTER DATA TABLE (Table 1) ---
        st.subheader("Table 1: Integrated Sample Metadata & Results")
        st.markdown("Full intersection of genomic variants and physical milk phenotypes.")
        st.dataframe(merged.style.background_gradient(subset=[trait], cmap='YlGnBu'), use_container_width=True)

        # Statistical Validation for Text Results
        r, p = stats.pearsonr(merged['nHomAlt'], merged[trait])
        st.markdown(f"**Scientific Summary:** A Pearson correlation of **r = {r:.3f}** was observed ($p = {p:.4e}$).")

        st.button("⬅️ Back to Quality Control", on_click=lambda: st.session_state.update({"stage": 1}))