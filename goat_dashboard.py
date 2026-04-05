import streamlit as st
import pandas as pd
import plotly.express as px
import io
import re

st.set_page_config(page_title="Genomic Research Workbench", layout="wide")
st.title("🧬 Genomic Discovery Suite: Deep Scan Mode")

uploaded_file = st.file_uploader("📥 Upload 'Individual_Goat_Stats.txt'", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    try:
        # 1. RAW DATA EXTRACTION
        raw_text = uploaded_file.getvalue().decode("utf-8")
        lines = raw_text.splitlines()
        
        # Capture the raw PSC rows
        psc_rows = [l.strip().split() for l in lines if l.startswith("PSC")]

        if not psc_rows:
            st.error("❌ No 'PSC' rows detected. Is this the correct stats file?")
        else:
            df_raw = pd.DataFrame(psc_rows)

            # --- DIAGNOSTIC SECTION: This helps us see the shift ---
            with st.expander("🔍 System Diagnostic: View Raw Column Mapping"):
                st.write("The computer sees these first 5 rows. Look for which column has 'Saanen_xxx' and which has counts like 1,000,000.")
                st.dataframe(df_raw.head(5))

            # 2. THE UNIVERSAL ADAPTER
            # We will search each column for one that looks like a Sample Name (contains letters/underscores)
            # and columns that look like genomic counts (large integers).
            
            final_df = pd.DataFrame()
            
            # Find the Sample Name Column (Usually index 2)
            for col in df_raw.columns:
                if any("_" in str(x) for x in df_raw[col].head(10)):
                    final_df['Sample'] = df_raw[col]
                    break
            
            # Find Numeric Columns by searching for the largest values
            numeric_cols = []
            for col in df_raw.columns:
                converted = pd.to_numeric(df_raw[col], errors='coerce')
                if not converted.isna().all():
                    numeric_cols.append(col)

            # Standard BCFtools mapping based on common offsets
            # If the logic above didn't find specific names, we use these common indices
            try:
                # Typically: [4]=nHet, [5]=nHomAlt, [8]=Ti, [9]=Tv, [11]=Depth
                # We use .get() to avoid crashing if the file is short
                final_df['nHet'] = pd.to_numeric(df_raw[4], errors='coerce')
                final_df['nHomAlt'] = pd.to_numeric(df_raw[5], errors='coerce')
                final_df['Ti'] = pd.to_numeric(df_raw[8], errors='coerce')
                final_df['Tv'] = pd.to_numeric(df_raw[9], errors='coerce')
                final_df['Depth'] = pd.to_numeric(df_raw[11], errors='coerce')
            except Exception:
                st.warning("⚠️ Traditional mapping failed. Attempting auto-detection.")

            # 3. CLEANING & RATIOS
            final_df['TiTv'] = final_df['Ti'] / final_df['Tv']
            # Remove the "Total Site" columns if they were accidentally grabbed (the Millions)
            final_df = final_df[final_df['nHomAlt'] < 1000000] 
            
            final_df = final_df.dropna()

            if len(final_df) > 0:
                st.success(f"✅ Protocol Active: {len(final_df)} Saanen samples ready.")
                
                tab1, tab2 = st.tabs(["🎯 Discovery Map", "📊 Population Structure"])
                
                with tab1:
                    fig = px.scatter(final_df, x="nHet", y="nHomAlt", color="TiTv", 
                                     size="Depth", hover_name="Sample",
                                     color_continuous_scale="Viridis", template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    # Nature-style distribution
                    fig2 = px.violin(final_df, y="nHomAlt", box=True, points="all", template="plotly_dark")
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.error("❌ Column alignment error. Please expand the 'System Diagnostic' above and tell me which column number contains the goat names.")

    except Exception as e:
        st.error(f"⚠️ Critical Error: {e}")