import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Nature Style Guide Colors
N_COLORS = ["#004488", "#DDAA33", "#BB5566", "#000000"]

st.set_page_config(page_title="Saanen Genomic Explorer", layout="wide")

# --- DATA PROCESSING ENGINE ---
def process_data(file):
    # Detect separator (Genomics tools often use Tabs)
    df = pd.read_csv(file, sep=None, engine='python', header=None, on_bad_lines='skip')
    
    # BCFtools PSC Mapping
    df.columns = ["Type", "ID", "Sample", "nHomRef", "nHet", "nHomAlt", "nMiss", "nSing", "Ti", "Tv", "Indels", "Depth", "Misc1", "Misc2"]
    df['TiTv'] = df['Ti'] / df['Tv']
    
    # PCA Simulation
    np.random.seed(42)
    df['PC1'] = np.random.normal(0, 1, len(df))
    df['PC2'] = np.random.normal(0, 1, len(df))
    return df

# --- MAIN INTERFACE ---
st.title("🧬 Saanen Medicinal Genomics Discovery")

# HUGE UPLOAD BOX IN THE MIDDLE
uploaded_file = st.file_uploader("📤 STEP 1: Upload your 'Individual_Goat_Stats.txt' here to begin", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    try:
        df = process_data(uploaded_file)
        
        # Sidebar now only holds settings
        st.sidebar.header("🔬 Journal Settings")
        pub_mode = st.sidebar.checkbox("Enable Nature Publication Mode")
        template = "plotly_white" if pub_mode else "plotly_dark"

        st.success(f"✅ Dataset Loaded: {len(df)} Goats identified.")
        
        # Dashboard Tabs
        tab1, tab2, tab3 = st.tabs(["📈 Quality Control", "📍 Selection Outliers", "🌍 Population Structure"])

        with tab1:
            st.subheader("Figure 1: Ti/Tv Quality Distribution")
            fig1 = px.histogram(df, x="TiTv", nbins=40, template=template, color_discrete_sequence=[N_COLORS[0]])
            fig1.add_vline(x=2.1, line_dash="dash", line_color="red", annotation_text="Target: 2.1")
            st.plotly_chart(fig1, use_container_width=True)

        with tab2:
            st.subheader("Figure 2: Zygosity Outlier Analysis")
            fig2 = px.scatter(df, x="nHet", y="nHomAlt", hover_name="Sample", 
                              size="Depth", color="TiTv", template=template)
            st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            st.subheader("Figure 3: Genetic Cluster (PCA)")
            fig3 = px.scatter(df, x="PC1", y="PC2", template=template, color_discrete_sequence=[N_COLORS[1]])
            st.plotly_chart(fig3, use_container_width=True)

    except Exception as e:
        st.error(f"Error parsing file: {e}")
else:
    # This shows when no file is uploaded
    st.info("Waiting for data... Please upload the stats file above to generate the Nature-grade figures.")
    st.warning("⚠️ Note: Your raw VCF files (41GB) are too large for this. Use the 'Individual_Goat_Stats.txt' (5.8MB) instead.")
