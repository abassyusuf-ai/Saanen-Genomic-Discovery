import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Medicinal Goat Explorer", layout="wide")
st.title("🧬 Genomic Discovery Dashboard: Saanen Goat Lineage")

# Load the data we just cleaned
@st.cache_data
def load_data():
    # Read the file and ignore lines that might be formatted incorrectly
    df = pd.read_csv("C:/Goat_Research/Goat_Stats_Clean.tsv", sep="\t", header=None, on_bad_lines='skip')
    
    # Dynamically name the first 6 essential columns
    # BCFtools PSC format: [1]Type [2]ID [3]Sample [4]nHomRef [5]nHet [6]nHomAlt
    new_names = {0: "Type", 1: "ID", 2: "Sample", 3: "nHomRef", 4: "nHet", 5: "nHomAlt"}
    df = df.rename(columns=new_names)
    
    # Convert numeric columns to ensure the plots work
    cols_to_fix = ["nHomRef", "nHet", "nHomAlt"]
    for col in cols_to_fix:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    return df.dropna(subset=["Sample", "nHomAlt"])
df = load_data()

# Summary Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Herd Size", len(df))
col2.metric("Max Homozygous Markers", f"{df['nHomAlt'].max():,}")
col3.metric("Min Homozygous Markers", f"{df['nHomAlt'].min():,}")

# The "Nature" Plot - Population Distribution
st.subheader("Population Genetic Diversity")
fig = px.scatter(df, x="nHet", y="nHomAlt", hover_name="Sample", 
                 color="nHomAlt", color_continuous_scale="Viridis",
                 labels={"nHet": "Heterozygous Sites", "nHomAlt": "Homozygous Alternate Sites"})
st.plotly_chart(fig, use_container_width=True)

# Top Candidate Selection
st.subheader("Elite Candidate Ranking")
top_10 = df.nlargest(10, 'nHomAlt')[['Sample', 'nHomAlt', 'nHet']]
st.table(top_10)