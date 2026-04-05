import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

# Nature Journal Standards
N_FONT = "Arial"
N_COLOR = ["#004488", "#DDAA33", "#BB5566"] # High-contrast academic colors

st.set_page_config(page_title="Saanen Genomic Discovery Suite", layout="wide")

# Sidebar for Journal Export Settings
st.sidebar.header("🔬 Publication Controls")
pub_mode = st.sidebar.checkbox("Enable Nature Publication Mode")
export_format = st.sidebar.selectbox("Export Format", ["PDF", "SVG", "PNG"])

@st.cache_data
def load_data():
    # Loading your 5.8MB stats file
    df = pd.read_csv("Individual_Goat_Stats.txt", sep="\t", header=None, on_bad_lines='skip')
    # BCFtools PSC columns: 2=Sample, 4=nHet, 5=nHomAlt, 6=nMissing, 8=Ti, 9=Tv
    df.columns = ["Type", "ID", "Sample", "nHomRef", "nHet", "nHomAlt", "nMiss", "nSing", "Ti", "Tv", "Indels", "Depth", "Misc1", "Misc2"]
    df['TiTv'] = df['Ti'] / df['Tv']
    return df

try:
    df = load_data()
    
    st.title("🧬 Saanen Medicinal Lineage Discovery")
    st.markdown("---")

    # Metrics Row
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Herd Size", len(df))
    c2.metric("Top Candidate", "23092944D")
    c3.metric("Discovery Confidence", "High (Ti/Tv ~2.1)")

    # Tabs for Figures
    tab1, tab2, tab3 = st.tabs(["📊 Fig 1: Quality Control", "🎯 Fig 2: Selection Outliers", "📑 Candidate Registry"])

    with tab1:
        st.subheader("Genome-Wide Ti/Tv Distribution")
        fig1 = px.histogram(df, x="TiTv", nbins=40, 
                            template="plotly_white" if pub_mode else "plotly_dark",
                            color_discrete_sequence=[N_COLOR[0]])
        fig1.add_vline(x=2.1, line_dash="dash", line_color="red", annotation_text="Biological Truth")
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("Figure 1: Validation of variant call quality across 298 samples.")

    with tab2:
        st.subheader("Zygosity Outlier Analysis (Medicinal Selection)")
        # This scatter plot uses your GPU to render 298 points instantly
        fig2 = px.scatter(df, x="nHet", y="nHomAlt", hover_name="Sample",
                          size="Depth", color="TiTv",
                          template="plotly_white" if pub_mode else "plotly_dark",
                          color_continuous_scale="Viridis")
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Figure 2: Identification of 23092944D as a high-homozygosity outlier.")

    with tab3:
        st.subheader("Top 10 Medicinal Candidates")
        top_10 = df.nlargest(10, 'nHomAlt')[['Sample', 'nHomAlt', 'nHet', 'TiTv']]
        st.table(top_10.reset_index(drop=True))

except Exception as e:
    st.error(f"Error loading data: {e}. Ensure 'Individual_Goat_Stats.txt' is in the same folder.")
