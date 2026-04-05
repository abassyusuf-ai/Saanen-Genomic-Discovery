import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="Genomic Research Workbench", layout="wide")
st.title("🧬 Precision Lineage & Variant Discovery Suite")

uploaded_file = st.file_uploader("📥 STEP 1: Upload 'Individual_Goat_Stats.txt'", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    try:
        # 1. READ RAW DATA
        raw_text = uploaded_file.getvalue().decode("utf-8")
        lines = raw_text.splitlines()
        psc_rows = [l.strip().split() for l in lines if l.startswith("PSC")]

        if not psc_rows:
            st.error("❌ No PSC rows found. Please check file content.")
        else:
            df_raw = pd.DataFrame(psc_rows)

            # 2. HARD-CODED MAPPING FROM DIAGNOSTIC DATA
            # Based on your latest screenshot (image_10ad85.png)
            final_df = pd.DataFrame()
            final_df['Sample'] = df_raw[2]
            final_df['nHet'] = pd.to_numeric(df_raw[4], errors='coerce')
            final_df['nHomAlt'] = pd.to_numeric(df_raw[5], errors='coerce')
            final_df['TiTv'] = pd.to_numeric(df_raw[9], errors='coerce')
            final_df['Depth'] = pd.to_numeric(df_raw[13], errors='coerce')

            # 3. CALCULATE HETEROZYGOSITY RATE (For Nature-style Violin Plots)
            final_df['Het_Rate'] = final_df['nHet'] / (final_df['nHet'] + final_df['nHomAlt'])
            
            # Clean up
            final_df = final_df.dropna()

            st.success(f"✅ Ingestion Complete: {len(final_df)} Saanen samples ready for Exploration.")

            # --- RESEARCH-GRADE VISUALS ---
            tab1, tab2 = st.tabs(["🛡️ Quality Audit", "🎯 Selection Pressure"])

            with tab1:
                st.markdown("### Figure 1: Technical Integrity (Ti/Tv)")
                # Validating the 41GB VCF processing accuracy
                fig1 = px.scatter(final_df, x="Depth", y="TiTv", hover_name="Sample", 
                                  template="plotly_dark", color_discrete_sequence=["#00CC96"])
                fig1.add_hline(y=2.1, line_dash="dash", line_color="red", annotation_text="Ideal Ti/Tv (2.1)")
                st.plotly_chart(fig1, use_container_width=True)

            with tab2:
                st.markdown("### Figure 2: Lineage Stabilization")
                st.info("Identifying high-homozygosity outliers for medicinal trait discovery.")
                # Replicating the scatter analysis from shared research papers
                fig2 = px.scatter(final_df, x="nHet", y="nHomAlt", color="TiTv", 
                                 size="Depth", hover_name="Sample", 
                                 color_continuous_scale="Viridis", template="plotly_dark")
                st.plotly_chart(fig2, use_container_width=True)
                
                # Adding the Violin Plot from your Nature-style reference
                st.markdown("### Figure 3: Population Heterozygosity Distribution")
                fig3 = px.violin(final_df, y="Het_Rate", box=True, points="all", 
                                hover_name="Sample", color_discrete_sequence=["#BB5566"],
                                template="plotly_dark")
                st.plotly_chart(fig3, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Critical System Error: {e}")