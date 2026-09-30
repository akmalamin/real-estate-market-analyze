"""
main.py — Real Estate Market & Investment Valuation CLI.

Usage:
    python main.py
"""

import os
import pandas as pd
from config import PROPERTY_DATA_PATH
from data.generate_property_data import generate_property_listings
from engine.roi_calculator import RealEstateCalculator


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║   🏡  REAL ESTATE MARKET & INVESTMENT ANALYZER — Day 116 ║
║   Cap Rates, Cashflow Underwriting & Geospatial Metrics  ║
╚══════════════════════════════════════════════════════════╝
    """)

    if not os.path.exists(PROPERTY_DATA_PATH):
        generate_property_listings()

    print(f"\n📂 Ingesting property listings: {PROPERTY_DATA_PATH}")
    df_raw = pd.read_csv(PROPERTY_DATA_PATH)

    # 1. Underwrite Properties (Financial & Mortgage Analysis)
    print("🧮 Calculating Cap Rates, Cash-on-Cash Returns & Net Cashflows...")
    df_underwritten = RealEstateCalculator.underwrite_properties(df_raw)

    # 2. Executive Market Summary
    summary = RealEstateCalculator.get_market_summary(df_underwritten)

    print(f"\n{'=' * 65}")
    print("📊 METRO REAL ESTATE MARKET SUMMARY")
    print(f"{'=' * 65}")
    print(f"   Total Properties Evaluated  : {summary['total_listings']}")
    print(f"   Median Property Price       : ${summary['median_price']:,.2f}")
    print(f"   Average Price per Sq Ft     : ${summary['avg_price_per_sqft']:,.2f}")
    print(f"   Average Market Cap Rate     : {summary['avg_cap_rate']:.2f}%")
    print(f"   Average Cash-on-Cash Return : {summary['avg_cash_on_cash']:.2f}%")
    print(f"   Average Monthly Rent        : ${summary['avg_monthly_rent']:,.2f}")
    print(f"   Positive Cashflow Deals     : {summary['profitable_deals_count']} / {summary['total_listings']}")

    print(f"\n🏆 TOP 5 HIGHEST CASH-FLOWING DEALS:")
    top_deals = df_underwritten.nlargest(5, "annual_net_cashflow")[
        ["address", "neighborhood", "property_type", "listing_price", "monthly_rent", "cap_rate_pct", "cash_on_cash_roi_pct", "monthly_net_cashflow"]
    ]
    print(top_deals.to_string(index=False))

    # 3. Save Detailed Underwriting Audit
    os.makedirs("output", exist_ok=True)
    out_path = "output/underwritten_real_estate_deals.csv"
    df_underwritten.to_csv(out_path, index=False)
    print(f"\n💾 Complete deal analysis exported → {out_path}")


if __name__ == "__main__":
    main()