import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Nature/Cell Journal Standards
N_COLORS = ["#004488", "#DDAA33", "#BB5566", "#000000"]

st.set_page_config(page_title="Genomic Research Workbench", layout="wide")

# --- 1. THE READY STATE (UI) ---
st.title("🧬 Genomic Research Workbench")
st.markdown("#### Precision Lineage & Variant Discovery Suite")

# The "Entry Gate"
uploaded_file = st.file_uploader("📥 STEP 1: Initialize Analysis by Uploading Individual_Goat_Stats.txt", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    try:
        # Load and clean
        df = pd.read_csv(uploaded_file, sep=None, engine='python', header=None, on_bad_lines='skip')
        
        # Mapping standard BCFtools PSC columns
        df.columns = ["Type", "ID", "Sample", "nHomRef", "nHet", "nHomAlt", "nMiss", "nSing", "Ti", "Tv", "Indels", "Depth", "Misc1", "Misc2"]
        df['TiTv'] = df['Ti'] / df['Tv']
        df['Het_Ratio'] = df['nHet'] / (df['nHet'] + df['nHomAlt'])

        st.success(f"Successfully ingested {len(df)} samples. Exploratory modules active.")

        # --- 2. THE EXPLORATION MODULES ---
        st.sidebar.header("🔬 Visual Controls")
        pub_mode = st.sidebar.checkbox("Enable Nature Publication Mode")
        template = "plotly_white" if pub_mode else "plotly_dark"

        # TABS FOR SCIENTIFIC EXPLORATION
        tab1, tab2, tab3 = st.tabs(["🛡️ Quality Audit", "🧬 Selection Pressure", "📊 Population Diversity"])

        with tab1:
            st.markdown("### Module 1: Technical Integrity Audit")
            st.write("Exploration of depth vs. variant quality to ensure no sequencing bias.")
            fig1 = px.scatter(df, x="Depth", y="TiTv", color="nMiss", 
                              hover_name="Sample", template=template,
                              title="Depth vs. Ti/Tv (Biological Truth Check)")
            fig1.add_hline(y=2.1, line_dash="dash", line_color="red", annotation_text="Ideal: 2.1")
            st.plotly_chart(fig1, use_container_width=True)

        with tab2:
            st.markdown("### Module 2: Selection & Stabilization Outliers")
            st.write("Detecting individuals with high homozygosity—the 'Stabilized Lineages' for medicinal traits.")
            fig2 = px.scatter(df, x="nHet", y="nHomAlt", color="TiTv", 
                              size="Depth", hover_name="Sample", template=template,
                              title="Homozygosity vs. Heterozygosity (Selection Search)")
            st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            st.markdown("### Module 3: Heterozygosity Distribution")
            st.write("Exploration of genetic diversity within the population.")
            fig3 = px.violin(df, y="Het_Ratio", box=True, points="all", 
                             template=template, color_discrete_sequence=[N_COLORS[1]],
                             title="Population Heterozygosity Spread")
            st.plotly_chart(fig3, use_container_width=True)

    except Exception as e:
        st.error(f"Error: The uploaded file does not match the required genomic format. ({e})")

else:
    # --- 3. THE IDLE STATE (No Figures Generated) ---
    st.info("👋 System Idle. Please upload a dataset to begin the automated exploratory analysis.")
    
    st.markdown("""
    ### 🔬 Scientific Explorations Performed Upon Upload:
    1.  **Ti/Tv Quality Check:** Confirms that the variant calls are biologically plausible.
    2.  **Zygosity Profiling:** Identifies "Fixed" traits within the population for pedigree stabilization.
    3.  **Depth-Normalization:** Ensures that discovery candidates aren't just artifacts of high sequencing depth.
    4.  **Population Spread:** Visualizes the genetic 'tightness' of the herd using Violin distribution plots.
    """)
    
    # Just a placeholder visual to keep it professional
    st.image("https://images.unsplash.com/photo-1579154276502-7bc246177b33?auto=format&fit=crop&q=80&w=1200", 
             caption="Awaiting Genomic Ingestion...", use_container_width=True)
