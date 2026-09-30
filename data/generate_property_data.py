"""data/generate_property_data.py — Generates realistic real estate listings with geospatial GPS data."""

import os
import random
import pandas as pd
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import PROPERTY_DATA_PATH, MAP_DEFAULT_LAT, MAP_DEFAULT_LON


def generate_property_listings(num_properties=250):
    print(f"🏡 Synthesizing {num_properties} property listings with geospatial coordinates...")

    property_types = ["Single Family Home", "Condo / Apartment", "Multi-Family (Duplex/Triplex)", "Townhouse"]
    neighborhoods = [
        ("Downtown / Central", 30.2672, -97.7431, 1.45),      # High Price
        ("South Congress / SoCo", 30.2450, -97.7520, 1.25),
        ("East Austin Arts District", 30.2620, -97.7180, 1.15),
        ("North Loop / Hyde Park", 30.3050, -97.7280, 1.05),
        ("Domain Tech District", 30.4020, -97.7250, 1.10),
        ("South Lamar / Barton Hills", 30.2480, -97.7850, 1.20),
        ("Westlake Hills Suburbs", 30.2980, -97.8050, 1.60),  # Luxury
        ("Riverside Metro Area", 30.2380, -97.7120, 0.85),    # High Yield
    ]

    data = []

    for i in range(1, num_properties + 1):
        prop_id = f"PROP-TX-{1000 + i}"
        neigh_name, center_lat, center_lon, price_multiplier = random.choice(neighborhoods)
        prop_type = random.choice(property_types)

        # Coordinate jitter within ~3 miles
        lat = center_lat + random.uniform(-0.025, 0.025)
        lon = center_lon + random.uniform(-0.025, 0.025)

        # Dimensions & Specs
        if prop_type == "Condo / Apartment":
            beds = random.choice([1, 2, 2, 3])
            baths = random.choice([1.0, 1.5, 2.0])
            sqft = random.randint(650, 1400)
            base_sqft_price = random.randint(380, 520)
        elif prop_type == "Single Family Home":
            beds = random.choice([3, 3, 4, 4, 5])
            baths = random.choice([2.0, 2.5, 3.0, 3.5])
            sqft = random.randint(1600, 3400)
            base_sqft_price = random.randint(310, 440)
        elif prop_type == "Multi-Family (Duplex/Triplex)":
            beds = random.choice([4, 6])
            baths = random.choice([3.0, 4.0])
            sqft = random.randint(2200, 4200)
            base_sqft_price = random.randint(280, 390)
        else: # Townhouse
            beds = random.choice([2, 3, 3])
            baths = random.choice([2.0, 2.5])
            sqft = random.randint(1300, 2100)
            base_sqft_price = random.randint(340, 460)

        year_built = random.randint(1985, 2024)
        price_per_sqft = int(base_sqft_price * price_multiplier * random.uniform(0.95, 1.05))
        listing_price = int(sqft * price_per_sqft)

        # Monthly Rent (Gross Yield typically 0.6% - 1.1% of purchase price monthly)
        rent_multiplier = random.uniform(0.0065, 0.0095)
        monthly_rent = int(listing_price * rent_multiplier)

        # Property condition rating (1-5)
        condition = random.choices([5, 4, 3, 2], weights=[30, 45, 20, 5])[0]
        hoa_monthly = random.choice([0, 0, 50, 180, 320]) if prop_type != "Single Family Home" else 0

        data.append({
            "property_id": prop_id,
            "address": f"{random.randint(100, 9999)} {random.choice(['Congress Ave', 'Lamar Blvd', 'Oak St', 'Cedar Ln', 'Barton Springs Rd', 'Riverside Dr', 'Guadalupe St'])}",
            "neighborhood": neigh_name,
            "property_type": prop_type,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "bedrooms": beds,
            "bathrooms": baths,
            "square_feet": sqft,
            "year_built": year_built,
            "price_per_sqft": price_per_sqft,
            "listing_price": listing_price,
            "monthly_rent": monthly_rent,
            "hoa_monthly": hoa_monthly,
            "condition_score": condition,
        })

    df = pd.DataFrame(data)
    df = df.sort_values(by="listing_price", ascending=False).reset_index(drop=True)

    os.makedirs(os.path.dirname(PROPERTY_DATA_PATH), exist_ok=True)
    df.to_csv(PROPERTY_DATA_PATH, index=False)
    print(f"✅ Generated property dataset ({len(df)} listings) at: {PROPERTY_DATA_PATH}")
    return df


if __name__ == "__main__":
    generate_property_listings()