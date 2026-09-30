"""
app.py — Interactive Real Estate Market Analyzer & Investment Dashboard.
Run: streamlit run app.py
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium

from config import PROPERTY_DATA_PATH
from data.generate_property_data import generate_property_listings
from engine.roi_calculator import RealEstateCalculator
from engine.geo_mapper import GeoMapper

st.set_page_config(
    page_title="EstatePulse Real Estate Intelligence",
    page_icon="🏡",
    layout="wide"
)

st.markdown("""
<style>
    .metric-card {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #334155;
        text-align: center;
    }
    .metric-val { font-size: 1.5rem; font-weight: 700; color: #F8FAFC; }
    .metric-lbl { font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_and_underwrite(down_payment_pct, interest_rate):
    if not os.path.exists(PROPERTY_DATA_PATH):
        generate_property_listings()
    df = pd.read_csv(PROPERTY_DATA_PATH)
    df = RealEstateCalculator.underwrite_properties(df, down_payment_pct, interest_rate)
    return df


# ---------------------------------------------------------
# SIDEBAR CONTROLS & UNDERWRITING ADJUSTMENTS
# ---------------------------------------------------------
st.sidebar.header("🕹️ Underwriting Assumptions")

down_payment_input = st.sidebar.slider("Down Payment (%)", min_value=10, max_value=50, value=20, step=5) / 100
interest_rate_input = st.sidebar.slider("Mortgage Interest Rate (%)", min_value=4.0, max_value=10.0, value=6.5,
                                        step=0.25) / 100

st.sidebar.markdown("---")
st.sidebar.header("🔍 Property Search Filters")

df_full = load_and_underwrite(down_payment_input, interest_rate_input)

# Price Filter
min_p, max_p = int(df_full["listing_price"].min()), int(df_full["listing_price"].max())
price_range = st.sidebar.slider("Price Range ($)", min_p, max_p, (min_p, max_p), step=25000)

# Property Types
all_types = sorted(df_full["property_type"].unique().tolist())
sel_types = st.sidebar.multiselect("Property Types", all_types, default=all_types)

# Neighborhoods
all_neighs = sorted(df_full["neighborhood"].unique().tolist())
sel_neighs = st.sidebar.multiselect("Neighborhoods", all_neighs, default=all_neighs)

# Min Cap Rate Filter
min_cap_rate = st.sidebar.slider("Minimum Cap Rate (%)", min_value=0.0, max_value=12.0, value=5.0, step=0.5)

# Filter Dataset
mask = (
        (df_full["listing_price"] >= price_range[0])
        & (df_full["listing_price"] <= price_range[1])
        & (df_full["property_type"].isin(sel_types))
        & (df_full["neighborhood"].isin(sel_neighs))
        & (df_full["cap_rate_pct"] >= min_cap_rate)
)
filtered_df = df_full.loc[mask]

# ---------------------------------------------------------
# MAIN DASHBOARD
# ---------------------------------------------------------
st.title("🏡 EstatePulse Real Estate Intelligence & Deal Analyzer")
st.caption("Underwriting Financial Metrics, Cap Rate Heatmaps & Cashflow Projections")

summary = RealEstateCalculator.get_market_summary(filtered_df)

c1, c2, c3, c4, c5, c6 = st.columns(6)
metrics = [
    ("Matching Listings", f"{summary.get('total_listings', 0):,}"),
    ("Median Price", f"${summary.get('median_price', 0):,.0f}"),
    ("Avg Price / SqFt", f"${summary.get('avg_price_per_sqft', 0):,.0f}"),
    ("Avg Cap Rate", f"{summary.get('avg_cap_rate', 0):.2f}%"),
    ("Avg Cash-on-Cash", f"{summary.get('avg_cash_on_cash', 0):.2f}%"),
    ("Cashflowing Deals", f"{summary.get('profitable_deals_count', 0):,}"),
]

for col, (label, val) in zip([c1, c2, c3, c4, c5, c6], metrics):
    col.markdown(
        f'<div class="metric-card"><div class="metric-lbl">{label}</div><div class="metric-val">{val}</div></div>',
        unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# TABS: MAPS, CHARTS & DEALS
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🗺️ Geospatial Property Map", "📊 Market Trends & Valuation", "📋 Deal Screener Table"])

with tab1:
    st.subheader("Geospatial Property Distribution & Cap Rate Map")
    if not filtered_df.empty:
        col_map_type = st.radio("Map Rendering Engine",
                                ["Plotly Heatmap (Fast)", "Leaflet Cluster Pins (Detailed Popups)"], horizontal=True)

        if "Plotly" in col_map_type:
            fig_map = GeoMapper.build_plotly_map(filtered_df, color_column="cap_rate_pct")
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            folium_map = GeoMapper.build_folium_cluster_map(filtered_df)
            st_folium(folium_map, width=1200, height=600)
    else:
        st.warning("No listings match your filter criteria. Try lowering the Cap Rate threshold.")

with tab2:
    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("Cap Rate vs. Listing Price")
        if not filtered_df.empty:
            fig_scatter = px.scatter(
                filtered_df,
                x="listing_price",
                y="cap_rate_pct",
                color="property_type",
                size="square_feet",
                hover_name="address",
                hover_data=["neighborhood", "monthly_rent", "monthly_net_cashflow"],
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_scatter.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(title="Purchase Price ($)", gridcolor="#334155"),
                yaxis=dict(title="Cap Rate (%)", gridcolor="#334155")
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    with col_r:
        st.subheader("Price per Sq Ft by Neighborhood")
        if not filtered_df.empty:
            sqft_df = filtered_df.groupby("neighborhood")["price_per_sqft"].mean().reset_index().sort_values(
                "price_per_sqft", ascending=True)
            fig_bar = px.bar(
                sqft_df,
                x="price_per_sqft",
                y="neighborhood",
                orientation="h",
                color="price_per_sqft",
                color_continuous_scale="Blues",
                text_auto=".0f"
            )
            fig_bar.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(title="Avg Price per Sq Ft ($)", gridcolor="#334155"),
                yaxis=dict(title=""),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)

with tab3:
    st.subheader("Investment Deal Screener")
    st.dataframe(
        filtered_df[[
            "property_id", "address", "neighborhood", "property_type", "listing_price",
            "monthly_rent", "cap_rate_pct", "cash_on_cash_roi_pct", "monthly_net_cashflow",
            "bedrooms", "bathrooms", "square_feet"
        ]],
        use_container_width=True
    )

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Underwritten Deals CSV",
        data=csv_data,
        file_name="real_estate_underwritten_deals.csv",
        mime="text/csv"
    )