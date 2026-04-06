import streamlit as st
import pandas as pd
import plotly.express as px
from scipy import stats

# --- PAGE CONFIG ---
st.set_page_config(page_title="Saanen Research Suite", layout="wide")

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

st.title("🧬 Saanen Lineage: Population vs. Elite Founders")
st.markdown("#### Comparative Analysis of Genetic Stability & Milk Quality")

# --- FILE INGESTION ---
col_u1, col_u2 = st.columns(2)
with col_u1:
    genomic_file = st.file_uploader("📥 STEP 1: genomic_stats.csv", type=['csv'])
with col_u2:
    pheno_file = st.file_uploader("📥 STEP 2: milk_phenotypes.csv", type=['csv'])

if genomic_file and pheno_file:
    try:
        # Load and Clean
        df_gen = pd.read_csv(genomic_file)
        df_pheno = pd.read_csv(pheno_file)
        
        df_gen.columns = df_gen.columns.str.strip()
        df_pheno.columns = df_pheno.columns.str.strip()
        
        df_gen['Sample'] = df_gen['Sample'].astype(str)
        df_pheno['Sample'] = df_pheno['Sample'].astype(str)
        
        # Merge datasets (298 goats)
        full_df = pd.merge(df_gen, df_pheno, on='Sample', how='inner')
        full_df['Het_Rate'] = full_df['nHet'] / (full_df['nHet'] + full_df['nHomAlt'])
        
        # --- SIDEBAR RESEARCH CONTROLS ---
        st.sidebar.header("🔬 Discovery Parameters")
        trait = st.sidebar.selectbox("Trait for Analysis:", [c for c in df_pheno.columns if c != 'Sample'])
        elite_count = st.sidebar.slider("Number of Elite Goats to Highlight:", 1, 50, 4)
        
        # Create the Elite Subset
        elite_df = full_df.sort_values(trait, ascending=False).head(elite_count)

        # --- DASHBOARD LAYOUT ---
        t1, t2, t3 = st.tabs(["🌍 Full Population (298)", "🏆 Elite Founders (Subset)", "📊 Genetic Gain Analysis"])

        with t1:
            st.subheader(f"Total Sample Population: {len(full_df)} Goats")
            # Image similar to your uploaded 'phy.png'
            fig_full = px.scatter(full_df, x="nHomAlt", y="nHet", color=trait, 
                                 size="Depth", hover_name="Sample", 
                                 color_continuous_scale="Viridis", template="plotly_dark",
                                 labels={"nHomAlt": "Homozygous Variants", "nHet": "Heterozygous Variants"})
            st.plotly_chart(fig_full, use_container_width=True)
            st.info("This view shows the full genetic diversity of the herd.")

        with t2:
            st.subheader(f"Top {elite_count} Elite Candidates for {trait}")
            # Highlight view with labels
            fig_elite = px.scatter(elite_df, x="nHomAlt", y="nHet", color=trait, 
                                  size="Depth", hover_name="Sample", text="Sample",
                                  color_continuous_scale="Viridis", template="plotly_dark")
            fig_elite.update_traces(textposition='top center')
            st.plotly_chart(fig_elite, use_container_width=True)
            
            st.write("**Selection Table:**")
            st.dataframe(elite_df[['Sample', 'nHomAlt', 'nHet', trait]], use_container_width=True)

        with t3:
            st.subheader("Breeding Impact & Correlation")
            
            # Impact Calculation
            pop_avg = full_df[trait].mean()
            elite_avg = elite_df[trait].mean()
            impact = ((elite_avg - pop_avg) / pop_avg) * 100
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Population Average", f"{pop_avg:.2f}")
            c2.metric(f"Elite {elite_count} Average", f"{elite_avg:.2f}")
            c3.metric("Predicted Genetic Gain", f"+{impact:.1f}%", delta_color="normal")
            
            # Correlation Analysis
            r, p = stats.pearsonr(full_df['nHomAlt'], full_df[trait])
            st.markdown(f"""
            **Scientific Findings:**
            - **Correlation Coefficient (r):** {r:.3f}
            - **Significance (p-value):** {p:.4f}
            """)
            
            if p < 0.05:
                st.success("✅ Statistically Significant: The genetic markers successfully predict milk quality.")
            else:
                st.warning("⚠️ Insight: Trend detected but requires more samples for statistical significance.")

    except Exception as e:
        st.error(f"⚠️ Research Error: {e}")
else:
    st.info("Upload genomic_stats.csv and milk_phenotypes.csv to generate the research report.")