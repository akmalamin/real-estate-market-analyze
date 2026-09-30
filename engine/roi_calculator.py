"""engine/roi_calculator.py — Cap Rate, Cash-on-Cash Return & Mortgage Amortization math."""

import pandas as pd
from config import (
    DEFAULT_DOWN_PAYMENT_PCT, DEFAULT_MORTGAGE_INTEREST_RATE, DEFAULT_LOAN_TERM_YEARS,
    DEFAULT_PROPERTY_TAX_PCT, DEFAULT_INSURANCE_ANNUAL, DEFAULT_MAINTENANCE_PCT, DEFAULT_VACANCY_RATE_PCT
)


class RealEstateCalculator:
    """Computes cashflow, Cap Rates, Cash-on-Cash return, and mortgage debt service."""

    @staticmethod
    def calculate_mortgage_payment(loan_amount, annual_interest_rate=DEFAULT_MORTGAGE_INTEREST_RATE, term_years=DEFAULT_LOAN_TERM_YEARS):
        """Monthly principal and interest payment calculation formula."""
        if loan_amount <= 0 or annual_interest_rate <= 0:
            return 0.0
        monthly_rate = annual_interest_rate / 12
        num_payments = term_years * 12
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        return float(monthly_payment)

    @classmethod
    def underwrite_properties(cls, df: pd.DataFrame, down_payment_pct=DEFAULT_DOWN_PAYMENT_PCT, interest_rate=DEFAULT_MORTGAGE_INTEREST_RATE) -> pd.DataFrame:
        """Batch evaluates financial metrics across every property in the dataset."""
        df = df.copy()

        # 1. Gross Annual Income
        df["annual_gross_rent"] = df["monthly_rent"] * 12

        # 2. Operating Expenses Breakdown
        df["vacancy_loss"] = df["annual_gross_rent"] * DEFAULT_VACANCY_RATE_PCT
        df["property_tax_annual"] = df["listing_price"] * DEFAULT_PROPERTY_TAX_PCT
        df["insurance_annual"] = DEFAULT_INSURANCE_ANNUAL
        df["maintenance_annual"] = df["listing_price"] * DEFAULT_MAINTENANCE_PCT
        df["hoa_annual"] = df["hoa_monthly"] * 12

        df["total_operating_expenses"] = (
            df["vacancy_loss"] + df["property_tax_annual"] + df["insurance_annual"] +
            df["maintenance_annual"] + df["hoa_annual"]
        )

        # 3. Net Operating Income (NOI) = Gross Income - Operating Expenses
        df["net_operating_income"] = (df["annual_gross_rent"] - df["total_operating_expenses"]).round(2)

        # 4. Cap Rate (%) = (NOI / Purchase Price) * 100
        df["cap_rate_pct"] = ((df["net_operating_income"] / df["listing_price"]) * 100).round(2)

        # 5. Financing & Mortgage Math
        df["down_payment_dollars"] = df["listing_price"] * down_payment_pct
        df["loan_amount"] = df["listing_price"] - df["down_payment_dollars"]

        df["monthly_mortgage_pi"] = df["loan_amount"].apply(lambda p: cls.calculate_mortgage_payment(p, interest_rate))
        df["annual_debt_service"] = df["monthly_mortgage_pi"] * 12

        # 6. Net Annual Cash Flow = NOI - Annual Debt Service
        df["annual_net_cashflow"] = (df["net_operating_income"] - df["annual_debt_service"]).round(2)
        df["monthly_net_cashflow"] = (df["annual_net_cashflow"] / 12).round(2)

        # 7. Cash-on-Cash Return (%) = (Annual Net Cash Flow / Total Cash Invested) * 100
        closing_costs = df["listing_price"] * 0.03  # 3% estimated closing costs
        total_cash_invested = df["down_payment_dollars"] + closing_costs
        df["cash_on_cash_roi_pct"] = ((df["annual_net_cashflow"] / total_cash_invested) * 100).round(2)

        # 8. Gross Rental Yield (%) = (Annual Rent / Purchase Price) * 100
        df["gross_rental_yield_pct"] = ((df["annual_gross_rent"] / df["listing_price"]) * 100).round(2)

        return df

    @staticmethod
    def get_market_summary(df: pd.DataFrame) -> dict:
        """High-level summary statistics for executive dashboards."""
        if df.empty:
            return {}

        return {
            "total_listings": len(df),
            "median_price": float(df["listing_price"].median()),
            "avg_price_per_sqft": float(df["price_per_sqft"].mean()),
            "avg_cap_rate": float(df["cap_rate_pct"].mean()),
            "avg_cash_on_cash": float(df["cash_on_cash_roi_pct"].mean()),
            "avg_monthly_rent": float(df["monthly_rent"].mean()),
            "profitable_deals_count": int((df["annual_net_cashflow"] > 0).sum()),
        }