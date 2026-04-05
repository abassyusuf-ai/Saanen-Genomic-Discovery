import streamlit as st
import pandas as pd
import plotly.express as px
import io
import re

st.set_page_config(page_title="Genomic Research Workbench", layout="wide")
st.title("🧬 Advanced Genomic Discovery Suite")

uploaded_file = st.file_uploader("📥 Upload 'Individual_Goat_Stats.txt'", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    try:
        # 1. READ FILE AND EXTRACT RAW LINES
        raw_bytes = uploaded_file.getvalue().decode("utf-8")
        lines = raw_bytes.splitlines()

        # 2. DEEP PARSING: FIND THE PSC HEADER AND DATA
        psc_header = None
        psc_data = []

        for line in lines:
            if line.startswith("# PSC"):
                # Clean the header: Remove '#', '[1]', '[2]' etc.
                clean_header = re.sub(r'\[\d+\]', '', line).replace('# ', '').strip()
                psc_header = re.split(r'\t|\s+', clean_header)
            elif line.startswith("PSC"):
                psc_data.append(re.split(r'\t|\s+', line.strip()))

        if not psc_header or not psc_data:
            st.error("❌ Failed to locate PSC (Per-Sample) section in the file.")
        else:
            # 3. BUILD DATAFRAME WITH DYNAMIC MAPPING
            df = pd.DataFrame(psc_data)
            
            # Match columns to header length
            df = df.iloc[:, :len(psc_header)]
            df.columns = psc_header

            # 4. CONVERT SCIENTIFIC COLUMNS
            # We use fuzzy matching to find columns even if named slightly differently
            def get_col(options):
                for opt in options:
                    for col in df.columns:
                        if opt.lower() in col.lower(): return col
                return None

            # Map the critical columns for your Saanen research
            col_map = {
                'nHet': get_col(['nHet', 'het']),
                'nHomAlt': get_col(['nHomAlt', 'hom_alt', 'nHoma']),
                'Ti': get_col(['Ti', 'ts']),
                'Tv': get_col(['Tv', 'tv']),
                'Depth': get_col(['average_depth', 'depth', 'dp']),
                'Sample': get_col(['sample', 'id'])
            }

            # Final Cleanup
            final_df = pd.DataFrame()
            for key, col_name in col_map.items():
                if col_name:
                    if key == 'Sample':
                        final_df[key] = df[col_name]
                    else:
                        final_df[key] = pd.to_numeric(df[col_name], errors='coerce')

            # 5. SCIENTIFIC CALCULATIONS
            final_df['TiTv'] = final_df['Ti'] / final_df['Tv']
            final_df = final_df.dropna(subset=['nHet', 'nHomAlt', 'TiTv'])

            # --- RESEARCH-GRADE VISUALS (REPLICATING YOUR SHARED IMAGES) ---
            st.success(f"✅ Deep Sync Complete: {len(final_df)} Saanen Genomes Mapped.")

            tab1, tab2, tab3 = st.tabs(["📊 Population Structure", "🎯 Discovery Map", "🔬 QC Metrics"])

            with tab1:
                st.markdown("### Population Heterozygosity (Nature Fig 1 Style)")
                # Replicates the density/violin plots from your reference images
                fig1 = px.violin(final_df, y="nHet", box=True, points="all", 
                               hover_name="Sample", color_discrete_sequence=["#BB5566"],
                               template="plotly_dark")
                st.plotly_chart(fig1, use_container_width=True)

            with tab2:
                st.markdown("### Selection Pressure (Stabilization Map)")
                # This identifies your medicinal founder goats
                fig2 = px.scatter(final_df, x="nHet", y="nHomAlt", color="TiTv", 
                                 size="Depth", hover_name="Sample", 
                                 color_continuous_scale="Viridis", template="plotly_dark")
                st.plotly_chart(fig2, use_container_width=True)

            with tab3:
                st.markdown("### Technical Integrity (Ti/Tv Audit)")
                fig3 = px.histogram(final_df, x="TiTv", nbins=20, template="plotly_dark")
                fig3.add_vline(x=2.1, line_dash="dash", line_color="red", annotation_text="Standard 2.1")
                st.plotly_chart(fig3, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Deep Parsing Failed: {e}")