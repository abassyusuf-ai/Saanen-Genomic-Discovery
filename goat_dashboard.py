import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="Genomic Research Workbench", layout="wide")
st.title("🧬 Genomic Research Workbench")

uploaded_file = st.file_uploader("📥 Upload 'Individual_Goat_Stats.txt'", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    try:
        # 1. READ RAW DATA AND FILTER FOR 'PSC' ROWS ONLY
        # This prevents the "Expected X fields, saw Y" error
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        psc_lines = [line for line in stringio if line.startswith("PSC")]

        if not psc_lines:
            st.error("❌ No 'PSC' rows found. Is this a standard bcftools stats file?")
        else:
            # 2. Convert filtered lines into a DataFrame
            # We use sep="\t" because BCFtools is tab-delimited
            df = pd.read_csv(io.StringIO("".join(psc_lines)), sep="\t", header=None)

            # 3. Apply the 14-column Schema
            # Mapping based on BCFtools PSC format
            schema = ["Type", "ID", "Sample", "nHomRef", "nHet", "nHomAlt", "nMiss", "nSing", "Ti", "Tv", "Indels", "Depth", "M1", "M2"]
            df.columns = schema[:len(df.columns)]

            # 4. Force Numeric Conversion
            cols_to_fix = ["nHomRef", "nHet", "nHomAlt", "nMiss", "Ti", "Tv", "Depth"]
            for col in cols_to_fix:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # 5. Scientific Calculations
            df['TiTv'] = df['Ti'] / df['Tv']
            df = df.dropna(subset=['TiTv'])

            st.success(f"✅ Ingestion Successful: {len(df)} Saanen samples ready.")

            # --- VISUALIZATION ---
            t1, t2 = st.tabs(["🛡️ Quality Audit", "🎯 Selection Pressure"])
            
            with t1:
                st.markdown("### Figure 1: Technical Integrity (Ti/Tv)")
                st.write("Ensuring the 41GB VCF processing maintained biological accuracy.")
                fig1 = px.scatter(df, x="Depth", y="TiTv", color="nMiss", 
                                  hover_name="Sample", template="plotly_dark",
                                  color_continuous_scale="Viridis")
                fig1.add_hline(y=2.1, line_dash="dash", line_color="red", annotation_text="Ideal Ti/Tv (2.1)")
                st.plotly_chart(fig1, use_container_width=True)

            with t2:
                st.markdown("### Figure 2: Lineage Stabilization")
                st.write("Identifying high-homozygosity outliers for medicinal trait discovery.")
                fig2 = px.scatter(df, x="nHet", y="nHomAlt", color="TiTv", 
                                  size="Depth", hover_name="Sample", template="plotly_dark")
                st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ System Error: {e}")
else:
    st.info("👋 System Idle. Please upload your stats file to begin exploration.")