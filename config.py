"""config.py — Real Estate investment benchmarks and geographic settings."""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROPERTY_DATA_PATH = os.path.join(DATA_DIR, "real_estate_listings.csv")

# Financial & Underwriting Defaults
DEFAULT_DOWN_PAYMENT_PCT = 0.20     # 20% Down Payment
DEFAULT_MORTGAGE_INTEREST_RATE = 0.065 # 6.5% 30-Year Fixed Loan
DEFAULT_LOAN_TERM_YEARS = 30
DEFAULT_PROPERTY_TAX_PCT = 0.0125   # 1.25% Annual Property Tax
DEFAULT_INSURANCE_ANNUAL = 1200.0   # $1,200/year Homeowners Insurance
DEFAULT_MAINTENANCE_PCT = 0.01      # 1.0% Annual Maintenance Reserve
DEFAULT_VACANCY_RATE_PCT = 0.05     # 5.0% Vacancy Allowance

# Regional Map Center (Austin, Texas Metro Area - Major Tech/Real Estate Hub)
MAP_DEFAULT_LAT = 30.2672
MAP_DEFAULT_LON = -97.7431
MAP_DEFAULT_ZOOM = 11