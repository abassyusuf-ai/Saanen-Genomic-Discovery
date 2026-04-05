import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="Genomic Research Workbench", layout="wide")
st.title("🧬 Advanced Genomic Discovery Suite")

uploaded_file = st.file_uploader("📥 Upload 'Individual_Goat_Stats.txt'", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    try:
        # 1. CAPTURE HEADER AND DATA
        content = uploaded_file.getvalue().decode("utf-8").splitlines()
        
        # Find the column definition line (usually starts with # PSC)
        header_line = [l for l in content if l.startswith("# PSC")][-1]
        columns = header_line.replace("# ", "").split("\t")
        
        # Capture the data lines
        data_rows = [l.split("\t") for l in content if l.startswith("PSC")]
        
        df = pd.DataFrame(data_rows, columns=columns)

        # 2. DYNAMIC MAPPING (The Fix)
        # This looks for the column names regardless of their position
        target_cols = {
            'Sample': ['sample', 'id', 'Sample'],
            'nHet': ['nHet', 'het', 'nhet'],
            'nHomAlt': ['nHomAlt', 'hom_alt', 'nhomalt'],
            'Ti': ['Ti', 'ts', 'transitions'],
            'Tv': ['Tv', 'tv', 'transversions'],
            'Depth': ['average_depth', 'depth', 'dp']
        }

        final_df = pd.DataFrame()
        for internal_name, aliases in target_cols.items():
            for alias in aliases:
                match = [c for c in df.columns if alias.lower() in c.lower()]
                if match:
                    final_df[internal_name] = pd.to_numeric(df[match[0]], errors='coerce')
                    break
        
        # Add Sample name separately as it's not numeric
        sample_col = [c for c in df.columns if "sample" in c.lower() or "id" in c.lower()]
        if sample_col:
            final_df['Sample'] = df[sample_col[0]]

        # 3. CALCULATIONS
        final_df['TiTv'] = final_df['Ti'] / final_df['Tv']
        final_df = final_df.dropna(subset=['nHet', 'nHomAlt', 'TiTv'])

        # --- REPLICATING RESEARCH FIGURES ---
        st.success(f"✅ Alignment Fixed: {len(final_df)} Saanen samples mapped.")

        tab1, tab2 = st.tabs(["📊 Population Structure", "🎯 Discovery Map"])

        with tab1:
            st.markdown("### Population Distribution (Nature Style)")
            # Replicating the "Violin" plots from your shared research
            fig1 = px.violin(final_df, y="nHomAlt", box=True, points="all", 
                            hover_name="Sample", color_discrete_sequence=["#BB5566"],
                            template="plotly_dark", title="Homozygosity Spread (Trait Stabilization)")
            st.plotly_chart(fig1, use_container_width=True)

        with tab2:
            st.markdown("### Stabilization Map (Selection Pressure)")
            # Replicating the scatter analysis
            fig2 = px.scatter(final_df, x="nHet", y="nHomAlt", color="TiTv", 
                             size="Depth", hover_name="Sample", 
                             color_continuous_scale="Viridis", template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Column Alignment Failed: {e}. Please ensure the file is a standard BCFtools stats output.")