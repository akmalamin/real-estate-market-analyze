# 🏡 EstatePulse: Real Estate Investment Market Analyzer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Framework: Streamlit](https://img.shields.io/badge/Framework-Streamlit-red.svg)]()
[![Maps: Folium & Plotly](https://img.shields.io/badge/Maps-Folium%20%7C%20Plotly-green.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An institutional-grade real estate analytics portal and investment property screener built in Python using Streamlit, Plotly, and Folium. Evaluates mortgage amortization debt service, Net Operating Income (NOI), Capitalization Rates, and Cash-on-Cash ROIs across residential and commercial property listings with interactive geospatial map clustering.

---

## 🌟 Key Capabilities

- **🧮 Dynamic Mortgage & Underwriting Math:** Interactive sliders for down payment % and interest rates recalculate debt service, net cashflows, and ROI on the fly.
- **🗺️ Dual Geospatial Mapping Engines:** Renders interactive Plotly Mapbox scatter layers and clustered Leaflet pins via Folium with detailed deal popups.
- **📈 Comprehensive Financial Metrics:** Computes Net Operating Income (NOI), Cap Rates, Gross Rental Yield, Price/SqFt, and Cash-on-Cash Return with vacancy and operating expense deductions.
- **🔍 Deal Screener & CSV Export:** Filter by minimum Cap Rate, budget, and neighborhood to identify high-cashflow deals.

---

## 🚀 Quick Start

```bash
# 1. Setup Virtual Environment
python -m venv venv
.\venv\Scripts\activate

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Launch Web Dashboard
streamlit run app.py