import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="Genomic Research Workbench", layout="wide")
st.title("🧬 Genomic Research Workbench")

uploaded_file = st.file_uploader("📥 Upload 'Individual_Goat_Stats.txt'", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    try:
        # 1. Filter the file for PSC lines
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        psc_lines = [line.strip() for line in stringio if line.startswith("PSC")]

        if not psc_lines:
            st.error("❌ No 'PSC' rows found. Check if the file contains sample stats.")
        else:
            # 2. Precision Parsing: use 'sep=r"\s+"' to handle multiple spaces/tabs
            df = pd.read_csv(io.StringIO("\n".join(psc_lines)), sep=r"\s+", header=None)

            # 3. Standard BCFtools PSC Mapping
            # Col 0:PSC, Col 1:ID, Col 2:Sample, Col 3:nHomRef, Col 4:nHet, Col 5:nHomAlt...
            schema = ["Type", "ID", "Sample", "nHomRef", "nHet", "nHomAlt", "nMiss", "nSing", "Ti", "Tv", "Indels", "Depth"]
            df = df.iloc[:, :len(schema)] # Keep only the columns we have names for
            df.columns = schema

            # 4. Force strict numeric conversion for the scientific columns
            for col in ["nHet", "nHomAlt", "Ti", "Tv", "Depth", "nMiss"]:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # 5. Scientific Metrics
            df['TiTv'] = df['Ti'] / df['Tv']
            # We drop only if both Ti and Tv are missing/zero to avoid empty charts
            df = df.dropna(subset=['Ti', 'Tv'])

            st.success(f"✅ Data Synchronized: {len(df)} Saanen goats detected.")

            # --- THE REAL VISUALS ---
            t1, t2 = st.tabs(["🛡️ Quality Audit", "🎯 Selection Pressure"])
            
            with t1:
                st.markdown("### Figure 1: Technical Integrity (Ti/Tv)")
                # If this plot is empty, it means Ti/Tv values are likely 0 or NaN
                fig1 = px.scatter(df, x="Depth", y="TiTv", color="nMiss", 
                                  hover_name="Sample", template="plotly_dark",
                                  title="Check: Are dots clustering near the 2.1 line?")
                fig1.add_hline(y=2.1, line_dash="dash", line_color="red")
                st.plotly_chart(fig1, use_container_width=True)

            with t2:
                st.markdown("### Figure 2: Lineage Stabilization")
                # We want to see a cloud of 298 dots here
                fig2 = px.scatter(df, x="nHet", y="nHomAlt", color="TiTv", 
                                  size="Depth", hover_name="Sample", template="plotly_dark",
                                  title="Discovery Map: High nHomAlt = Stabilized Traits")
                st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ System Error: {e}")
else:
    st.info("👋 System Ready. Please upload your stats file to begin.")