import pandas as pd
import numpy as np
import psycopg2
from sqlalchemy import create_engine
import random

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'grunental_db',
    'user': 'postgres',
    'password': '12345'
}

def get_engine():
    return create_engine(f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}")

def generate_data():
    engine = get_engine()
    
    # Dimensions with higher variance for non-symmetrical scenario
    areas = [
        {"name": "Comercial", "weight": 2.2},
        {"name": "Marketing", "weight": 1.6},
        {"name": "R&D", "weight": 1.1},
        {"name": "Supply Chain", "weight": 0.7},
        {"name": "Regulatory", "weight": 0.4},
        {"name": "Admin & HR", "weight": 0.2}
    ]
    products = ["Zytram", "Palexia", "Tramal", "Versatis", "Arcoxia", "Qutenza"]
    months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    
    countries = [
        {"name": "USA", "iso": "USA", "region": "North America", "market_weight": 3.5},
        {"name": "Germany", "iso": "DEU", "region": "Europe", "market_weight": 2.0},
        {"name": "Brazil", "iso": "BRA", "region": "LATAM", "market_weight": 1.8},
        {"name": "Mexico", "iso": "MEX", "region": "LATAM", "market_weight": 1.5},
        {"name": "Italy", "iso": "ITA", "region": "Europe", "market_weight": 1.2},
        {"name": "Spain", "iso": "ESP", "region": "Europe", "market_weight": 1.0},
        {"name": "Colombia", "iso": "COL", "region": "LATAM", "market_weight": 0.8},
        {"name": "Peru", "iso": "PER", "region": "LATAM", "market_weight": 0.5},
        {"name": "Chile", "iso": "CHL", "region": "LATAM", "market_weight": 0.4},
        {"name": "Ecuador", "iso": "ECU", "region": "LATAM", "market_weight": 0.3}
    ]
    
    # 1. Performance Data (The Master Table)
    # This table will contain EVERYTHING to ensure filters update ALL charts.
    master_data = []
    
    # Sum of market weights for normalization if needed
    total_weight = sum(c['market_weight'] for c in countries) # ~13.0
    # Average area weight for normalization
    avg_area_weight = sum(a['weight'] for a in areas) / len(areas) # ~0.9
    
    for country in countries:
        for area in areas:
            for product in products:
                for i, month in enumerate(months):
                    # Market influence factor based on population/importance
                    market_factor = country['market_weight']
                    
                    # Area influence factor to differentiate BU Execution
                    area_factor = area['weight'] / avg_area_weight
                    
                    # Target aggregate sales range (total sum of all countries per month):
                    # Jan: ~6M, Dec: ~10M
                    # Total records per month = 360 (10 countries * 6 areas * 6 products)
                    # To get 6M total in Jan, the average record value is ~16,666.
                    # We distribute this average based on the country's market_weight and area weight.
                    avg_weight = total_weight / len(countries) # 1.3
                    weight_mult = (market_factor / avg_weight) * area_factor
                    
                    # Monthly base growth (linear from Jan to Dec)
                    month_growth_factor = (i / 11.0)
                    base_sales_avg = 13000 + (month_growth_factor * (21000 - 13000))
                    
                    # Slight fluctuations per month (+/- 8%)
                    month_fluctuation = random.uniform(0.92, 1.08)
                    
                    # Generate coherent numbers proportional to population/market and BU weight
                    # Reduced random variance per record to 2% to preserve the BU weight dominance
                    sales_vol = (base_sales_avg * weight_mult * month_fluctuation) * random.uniform(0.98, 1.02)
                    budget_exp = sales_vol * random.uniform(0.28, 0.35) # 28-35% of sales
                    actual_exp = budget_exp * random.uniform(0.95, 1.05) # Lower variance for clear ranking
                    income = sales_vol * random.uniform(0.2, 0.4)
                    bills = actual_exp * random.uniform(0.7, 0.85)
                    
                    master_data.append({
                        'country': country['name'],
                        'iso_alpha': country['iso'],
                        'region': country['region'],
                        'area': area['name'],
                        'product': product,
                        'month': month,
                        'month_idx': i + 1,
                        'sales_volume': sales_vol,
                        'actual_expenses': actual_exp,
                        'budget_expenses': budget_exp,
                        'income': income,
                        'bills': bills
                    })
    
    df_master = pd.DataFrame(master_data)
    df_master.to_sql('master_performance', engine, if_exists='replace', index=False)
    
    # 2. Fixed Allocation Table (Departments don't change by country for this MVP logic)
    allocation_data = {
        'department': ['R&D', 'OpEx', 'Admin', 'Marketing'],
        'percentage': [45, 30, 15, 10]
    }
    pd.DataFrame(allocation_data).to_sql('allocation_summary', engine, if_exists='replace', index=False)
    
    # 3. Fixed Cost Centers Table
    highest_expenses = {
        'cost_center': ['Clinical Trials Ph. III', 'Supply Logistics EU', 'Global HR Systems', 'Marketing Campaign Q4'],
        'amount': [125000, 85000, 45000, 32000]
    }
    pd.DataFrame(highest_expenses).to_sql('highest_expenses', engine, if_exists='replace', index=False)

    print("Multidimensional Master Data generated and uploaded to PostgreSQL.")

if __name__ == "__main__":
    try:
        conn = psycopg2.connect(dbname='postgres', user=DB_CONFIG['user'], password=DB_CONFIG['password'], host=DB_CONFIG['host'])
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_CONFIG['database']}'")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
        cur.close()
        conn.close()
        generate_data()
    except Exception as e:
        print(f"Error: {e}")
        generate_data()
