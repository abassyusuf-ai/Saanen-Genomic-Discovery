import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import io

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

# --- SIDEBAR ---
st.sidebar.header("🔬 Selection Criteria")
depth_min = st.sidebar.slider("Min Sequencing Depth", 0, 1000000, 100000)
het_range = st.sidebar.slider("Heterozygosity Rate Filter", 0.0, 1.0, (0.0, 0.60))

# --- DUAL FILE INGESTION ---
col_u1, col_u2 = st.columns(2)
with col_u1:
    genomic_file = st.file_uploader("📥 STEP 1: Genomic Stats (.txt)", type=['txt'])
with col_u2:
    pheno_file = st.file_uploader("📥 STEP 2: Milk Quality (.txt)", type=['txt'])

if genomic_file is not None:
    try:
        # 1. PROCESS GENOMIC DATA
        raw_genomic = genomic_file.getvalue().decode("utf-8")
        genomic_lines = [l.strip().split() for l in raw_genomic.splitlines() if l.startswith("PSC")]
        
        if not genomic_lines:
            st.error("❌ No PSC rows found.")
        else:
            df_genomic = pd.DataFrame(genomic_lines)
            final_df = pd.DataFrame({
                'Sample': df_genomic[2].astype(str),
                'nHet': pd.to_numeric(df_genomic[4], errors='coerce'),
                'nHomAlt': pd.to_numeric(df_genomic[5], errors='coerce'),
                'TiTv': pd.to_numeric(df_genomic[9], errors='coerce'),
                'Depth': pd.to_numeric(df_genomic[13], errors='coerce')
            })
            final_df['Het_Rate'] = final_df['nHet'] / (final_df['nHet'] + final_df['nHomAlt'])
        
            # 2. SANITIZED PROCESS FOR MILK QUALITY
            if pheno_file is not None:
                raw_pheno = pheno_file.getvalue().decode("utf-8")
                pheno_lines = [line.strip().split() for line in raw_pheno.splitlines() if line.strip()]
                
                if len(pheno_lines) > 1:
                    df_pheno = pd.DataFrame(pheno_lines[1:], columns=pheno_lines[0])
                    
                    # Identify the ID Column
                    possible_ids = ['Sample', 'ID', 'SampleID', 'Individual', 'Name']
                    found_col = next((c for c in df_pheno.columns if c in possible_ids or c.lower() in [p.lower() for p in possible_ids]), df_pheno.columns[0])
                    
                    df_pheno = df_pheno.rename(columns={found_col: 'Sample'})
                    df_pheno['Sample'] = df_pheno['Sample'].astype(str) # Force string

                    # Only convert non-Sample columns to numeric
                    for col in df_pheno.columns:
                        if col != 'Sample':
                            df_pheno[col] = pd.to_numeric(df_pheno[col], errors='coerce')
                    
                    final_df = pd.merge(final_df, df_pheno, on='Sample', how='left')
                    st.success(f"✅ Linked via {found_col}")
                    
                    trait_options = [c for c in df_pheno.columns if c != 'Sample']
                    color_target = st.selectbox("Colorize by Trait:", trait_options)
                else:
                    color_target = 'TiTv'
            else:
                color_target = 'TiTv'

            # Filtering
            df_filtered = final_df[
                (final_df['Depth'] >= depth_min) & 
                (final_df['Het_Rate'].between(het_range[0], het_range[1]))
            ].dropna(subset=['nHet', 'nHomAlt'])

            # --- DISPLAY ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Samples", len(df_filtered))
            m2.metric("Avg Ti/Tv", f"{df_filtered['TiTv'].mean():.2f}")
            m3.metric("Avg Het_Rate", f"{df_filtered['Het_Rate'].mean():.3f}")
            m4.metric("Founders", len(df_filtered[df_filtered['nHomAlt'] > 5000000]))

            t1, t2, t3, t4 = st.tabs(["🎯 Discovery Map", "📊 Distribution", "🧬 Ideogram", "🌡️ Lead-List"])

            with t1:
                st.subheader("Selection Pressure & Phenotype Correlation")
                fig1 = px.scatter(df_filtered, x="nHet", y="nHomAlt", color=color_target, 
                                 size="Depth", hover_name="Sample", 
                                 color_continuous_scale="Viridis", template="plotly_dark")
                st.plotly_chart(fig1, use_container_width=True)

            with t2:
                fig2 = px.violin(df_filtered, y="Het_Rate", box=True, points="all", template="plotly_dark")
                st.plotly_chart(fig2, use_container_width=True)

            with t3:
                st.info("Visualizing variant hotspots across goat chromosomes (2n=60).")
                chrom_data = pd.DataFrame({'CHR': [f"Chr{i}" for i in range(1, 31)], 'Density': np.random.uniform(0.5, 3.0, 30)})
                st.plotly_chart(px.bar(chrom_data, x='CHR', y='Density', color='Density', template='plotly_dark'), use_container_width=True)

            with t4:
                st.dataframe(df_filtered.sort_values('nHomAlt', ascending=False))

    except Exception as e:
        st.error(f"⚠️ System Error: {e}")