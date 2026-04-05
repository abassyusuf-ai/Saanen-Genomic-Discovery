# Genomic Discovery of Medicinal Traits in Saanen Goats 
**Status:** In-Preparation for *Nature* / Scientific Review

This repository contains the computational pipeline and discovery dataset used to identify high-homozygosity outliers within a population of 298 Saanen goats, specifically targeting markers for eczema-healing milk properties (Casein & Lactoferrin).

## Key Discovery: Candidate 23092944D
Our analysis identified **Goat 23092944D** as a primary candidate for medicinal lineage stabilization, boasting **7,387,838 Homozygous Alternate sites** with a biologically validated Ti/Tv ratio of ~2.1.

## Interactive Dashboard
The included `goat_dashboard.py` is a Streamlit-based suite designed for NVIDIA-accelerated visualization of:
- **Zygosity Outliers:** Identifying "Genetically Pure" candidates.
- **Quality Metrics:** Ti/Tv distributions and Missingness maps.
- **Breed Purity:** PCA clustering of the Saanen population.

## How to Reproduce
1. Clone the repo: `git clone https://github.com/abassyusuf-ai/Saanen-Genomic-Discovery.git`
2. Install dependencies: `pip install streamlit pandas plotly`
3. Run the suite: `streamlit run goat_dashboard.py`
