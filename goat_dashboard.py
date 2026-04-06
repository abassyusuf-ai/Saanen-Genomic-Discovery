import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import numpy as np

# --- PUBLICATION STANDARDS ---
T, G_P, T_P, D_P, M_P = "plotly_white", px.colors.sequential.Viridis, px.colors.sequential.Plasma, px.colors.sequential.Magma, "RdYlGn"
st.set_page_config(page_title="Saanen Suite", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("<style>.stButton>button { background-color: #004d40; color: white; font-weight: bold; }</style>", unsafe_allow_html=True)

# --- NAVIGATION ---
if 'p' not in st.session_state: st.session_state.p = 1
def go(n): st.session_state.p = n

st.sidebar.title("🔬 Objectives")
for i in range(1, 5):
    if st.sidebar.button(f"Phase {i}: Objective {i}"): go(i)
if st.sidebar.button("🔄 Reset"): st.session_state.clear(); st.rerun()

st.title(f"📊 Saanen Genomic Analysis: Phase {st.session_state.p}")
st.caption("Objectives 1-4 | Standardized Scientific Workflow")
st.divider()

# --- DATA LOADER HELPER ---
def load_and_merge(k1, k2=None):
    g = st.file_uploader("📂 Genomic CSV", type='csv', key=k1)
    p = st.file_uploader("📥 Phenotype CSV", type='csv', key=k2) if k2 else None
    if g and (not k2 or p):
        df_g = pd.read_csv(g).rename(columns=lambda x: x.strip())
        df_g['Sample'] = df_g['Sample'].astype(str).str.strip()
        if not k2: return df_g
        df_p = pd.read_csv(p).rename(columns=lambda x: x.strip())
        df_p['Sample'] = df_p['Sample'].astype(str).str.strip()
        return pd.merge(df_g, df_p, on='Sample', how='inner')
    return None

# --- PHASE LOGIC ---
if st.session_state.p == 1:
    df = load_and_merge("g1")
    if df is not None:
        df['HR'] = df['nHet'] / (df['nHet'] + df['nHomAlt'])
        c1, c2 = st.columns([2, 1])
        c1.plotly_chart(px.scatter(df, x="nHomAlt", y="nHet", color="TiTv", size="Depth", template=T, color_continuous_scale=G_P), use_container_width=True)
        c2.plotly_chart(px.violin(df, y="HR", box=True, points="all", template=T), use_container_width=True)
        st.button("Next Phase ➡️", on_click=lambda: go(2))

elif st.session_state.p == 2:
    df = load_and_merge("g2", "p2")
    if df is not None:
        st.dataframe(df.style.background_gradient(cmap='YlGnBu'), use_container_width=True)
        tr = st.selectbox("Select Trait:", [c for c in df.columns if c not in ['Sample', 'nHet', 'nHomAlt', 'TiTv', 'Depth']])
        st.plotly_chart(px.bar(df, x="Sample", y=tr, color=tr, template=T, color_continuous_scale=T_P), use_container_width=True)
        st.button("Next Phase ➡️", on_click=lambda: go(3))

elif st.session_state.p == 3:
    df = load_and_merge("g3", "p3")
    if df is not None:
        tr = st.selectbox("Target:", [c for c in df.columns if c not in ['Sample', 'nHet', 'nHomAlt', 'TiTv', 'Depth']])
        m, b, r, p, _ = stats.linregress(df['nHomAlt'], df[tr])
        fig = px.scatter(df, x="nHomAlt", y=tr, color="nHet", size="Depth", template=T, color_continuous_scale=D_P)
        fig.add_trace(go.Scatter(x=df['nHomAlt'], y=m*df['nHomAlt']+b, mode='lines', name='OLS Line', line=dict(color='red')))
        st.plotly_chart(fig, use_container_width=True)
        cols = st.columns(3)
        cols[0].metric("Corr (r)", f"{r:.3f}"); cols[1].metric("P-Val", f"{p:.4e}"); cols[2].metric("N", len(df))
        st.button("Next Phase ➡️", on_click=lambda: go(4))

elif st.session_state.p == 4:
    df = load_and_merge("g4", "p4")
    if df is not None:
        tr = st.selectbox("Breeding Goal:", [c for c in df.columns if c not in ['Sample', 'nHet', 'nHomAlt', 'TiTv', 'Depth']])
        # --- MERIT MATH ---
        df['MS'] = (df[tr]/df[tr].max()) - (df['nHomAlt']/df['nHomAlt'].max())
        # --- SIZE FIX: Ensure always positive for Plotly ---
        df['Display_Size'] = df['MS'] - df['MS'].min() + 0.1 
        
        c1, c2 = st.columns([2, 1])
        with c1:
            fig4 = px.scatter(df, x="nHomAlt", y=tr, size="Display_Size", color="MS", hover_name="Sample", 
                              color_continuous_scale=M_P, template=T, title="Selection Pressure Map")
            st.plotly_chart(fig4, use_container_width=True)
        with c2:
            st.write("### Elite Candidates")
            for _, row in df.sort_values("MS", ascending=False).head(5).iterrows():
                st.metric(f"ID: {row['Sample']}", f"Merit: {row['MS']:.3f}")