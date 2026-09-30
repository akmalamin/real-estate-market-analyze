"""engine/geo_mapper.py — Interactive geospatial pricing & cap rate visualizations."""

import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from config import MAP_DEFAULT_LAT, MAP_DEFAULT_LON, MAP_DEFAULT_ZOOM


class GeoMapper:
    """Generates interactive Plotly and Folium real estate maps."""

    @staticmethod
    def build_plotly_map(df, color_column="cap_rate_pct", size_column="listing_price"):
        """Fast interactive Map/Mapbox scatter map with universal Plotly version compatibility."""
        if df.empty:
            return None

        # Automatic detection for Plotly 5.x vs 6.x naming
        try:
            if hasattr(px, "scatter_map"):
                fig = px.scatter_map(
                    df,
                    lat="latitude",
                    lon="longitude",
                    color=color_column,
                    size=size_column,
                    hover_name="address",
                    hover_data=["neighborhood", "property_type", "listing_price", "monthly_rent", "cap_rate_pct", "cash_on_cash_roi_pct"],
                    color_continuous_scale="Viridis",
                    zoom=MAP_DEFAULT_ZOOM,
                    center={"lat": MAP_DEFAULT_LAT, "lon": MAP_DEFAULT_LON},
                    height=600,
                )
            else:
                fig = px.scatter_mapbox(
                    df,
                    lat="latitude",
                    lon="longitude",
                    color=color_column,
                    size=size_column,
                    hover_name="address",
                    hover_data=["neighborhood", "property_type", "listing_price", "monthly_rent", "cap_rate_pct", "cash_on_cash_roi_pct"],
                    color_continuous_scale="Viridis",
                    zoom=MAP_DEFAULT_ZOOM,
                    center={"lat": MAP_DEFAULT_LAT, "lon": MAP_DEFAULT_LON},
                    mapbox_style="open-street-map",
                    height=600,
                )
        except Exception:
            # Fallback to standard open-street-map
            fig = px.scatter_mapbox(
                df,
                lat="latitude",
                lon="longitude",
                color=color_column,
                size=size_column,
                hover_name="address",
                hover_data=["neighborhood", "property_type", "listing_price", "monthly_rent", "cap_rate_pct"],
                color_continuous_scale="Viridis",
                zoom=MAP_DEFAULT_ZOOM,
                center={"lat": MAP_DEFAULT_LAT, "lon": MAP_DEFAULT_LON},
                mapbox_style="open-street-map",
                height=600,
            )

        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_colorbar=dict(title=color_column.replace("_", " ").title())
        )
        return fig

    @staticmethod
    def build_folium_cluster_map(df):
        """Generates interactive Leaflet.js marker cluster map with popups."""
        m = folium.Map(location=[MAP_DEFAULT_LAT, MAP_DEFAULT_LON], zoom_start=MAP_DEFAULT_ZOOM, tiles="CartoDB positron")
        marker_cluster = MarkerCluster().add_to(m)

        for _, row in df.iterrows():
            cap = row["cap_rate_pct"]
            pin_color = "green" if cap >= 7.0 else "blue" if cap >= 5.0 else "red"

            popup_html = f"""
            <div style='font-family: Arial, sans-serif; min-width: 200px;'>
                <h4 style='margin:0 0 5px 0; color:#1A365D;'>{row['address']}</h4>
                <b>Price:</b> ${row['listing_price']:,}<br/>
                <b>Type:</b> {row['property_type']}<br/>
                <b>Monthly Rent:</b> ${row['monthly_rent']:,}/mo<br/>
                <b>Cap Rate:</b> <span style='color:green; font-weight:bold;'>{row['cap_rate_pct']}%</span><br/>
                <b>Cash-on-Cash:</b> {row['cash_on_cash_roi_pct']}%<br/>
                <b>Monthly Net Cashflow:</b> ${row['monthly_net_cashflow']:,.2f}
            </div>
            """

            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{row['address']} (${row['listing_price']:,} | Cap: {cap}%)",
                icon=folium.Icon(color=pin_color, icon="home", prefix="fa"),
            ).add_to(marker_cluster)

        return m