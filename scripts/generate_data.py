import psycopg2
import logging
import random
from datetime import datetime, timedelta
from faker import Faker
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
fake = Faker()

# Database connection parameters
db_params = {
    'dbname': 'porsche_analytics',
    'user': 'porsche_admin',
    'password': 'p0rsch3_secret',
    'host': 'localhost',
    'port': '5432'
}

# Porsche-specific data
porsche_models = [
    ('911 Carrera', 'P-911-CR', 1963, None, 'Sports Car', 101200.00, 379, 'Coupe', False, 'Iconic rear-engine sports car'),
    ('911 Turbo S', 'P-911-TS', 1975, None, 'Sports Car', 207000.00, 640, 'Coupe', False, 'High-performance variant of the 911'),
    ('Taycan', 'P-TAY', 2019, None, 'Sedan', 86700.00, 522, 'Sedan', True, 'All-electric four-door sports car'),
    ('Panamera', 'P-PAN', 2009, None, 'Luxury', 88400.00, 325, 'Sedan', False, 'Four-door luxury sports car'),
    ('Cayenne', 'P-CAY', 2002, None, 'SUV', 69000.00, 335, 'SUV', False, 'Mid-size luxury crossover SUV'),
    ('Macan', 'P-MAC', 2014, None, 'SUV', 54900.00, 248, 'SUV', False, 'Compact luxury crossover SUV'),
    ('718 Boxster', 'P-BOX', 1996, None, 'Sports Car', 62000.00, 300, 'Convertible', False, 'Mid-engine two-seater roadster'),
    ('718 Cayman', 'P-CAY', 2005, None, 'Sports Car', 60500.00, 300, 'Coupe', False, 'Mid-engine two-seater coupe'),
    ('Taycan Cross Turismo', 'P-TAYCT', 2021, None, 'Wagon', 93700.00, 469, 'Wagon', True, 'All-electric wagon variant of the Taycan'),
    ('Cayenne Coupe', 'P-CAYC', 2019, None, 'SUV', 76500.00, 335, 'SUV Coupe', False, 'Coupe variant of the Cayenne SUV'),
    ('911 GT3', 'P-911-GT3', 1999, None, 'Sports Car', 161100.00, 502, 'Coupe', False, 'High-performance variant of the 911'),
    ('918 Spyder', 'P-918', 2013, 2015, 'Hypercar', 845000.00, 887, 'Convertible', True, 'Limited production hybrid sports car'),
    ('Carrera GT', 'P-CGT', 2003, 2007, 'Supercar', 448000.00, 605, 'Convertible', False, 'Mid-engine sports car')
]

regions = ['North America', 'Europe', 'Asia Pacific', 'Middle East', 'South America']
countries = {
    'North America': ['United States', 'Canada', 'Mexico'],
    'Europe': ['Germany', 'United Kingdom', 'France', 'Italy', 'Switzerland', 'Netherlands', 'Spain'],
    'Asia Pacific': ['China', 'Japan', 'Australia', 'South Korea', 'Singapore'],
    'Middle East': ['United Arab Emirates', 'Saudi Arabia', 'Qatar', 'Kuwait'],
    'South America': ['Brazil', 'Argentina', 'Chile', 'Colombia']
}

# Generate a list of VINs to ensure uniqueness
def generate_vins(count=300):
    vins = set()
    while len(vins) < count:
        vin = 'WP0' + ''.join(random.choices('ABCDEFGHJKLMNPRSTUVWXYZ0123456789', k=14))
        vins.add(vin)
    return list(vins)

# Insert data into models table
def insert_models(cur):
    logger.info("Inserting data into models table...")
    models_sql = """
        INSERT INTO models (model_name, model_code, production_start_year, production_end_year, 
                            segment, base_price, horsepower, body_type, is_electric, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING model_id
    """
    model_ids = []
    for model_data in porsche_models:
        cur.execute(models_sql, model_data)
        model_ids.append(cur.fetchone()[0])
    
    logger.info(f"Inserted {len(model_ids)} models")
    return model_ids

# Insert data into dealerships table
def insert_dealerships(cur):
    logger.info("Inserting data into dealerships table...")
    dealerships_sql = """
        INSERT INTO dealerships (name, address, city, country, region, opening_date, 
                                 service_center, sales_capacity, rating, manager_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING dealership_id
    """
    dealership_ids = []
    
    # Insert at least 50 dealerships
    for _ in range(50):
        region = random.choice(regions)
        country = random.choice(countries[region])
        city = fake.city()
        
        name = f"Porsche {city}"
        address = fake.address().replace("\n", ", ")
        opening_date = fake.date_between(start_date='-30y', end_date='today')
        service_center = random.random() > 0.1  # 90% have service centers
        sales_capacity = random.randint(10, 50)
        rating = round(random.uniform(3.0, 5.0), 2)
        manager_name = fake.name()
        
        dealership_data = (name, address, city, country, region, opening_date, 
                          service_center, sales_capacity, rating, manager_name)
        
        cur.execute(dealerships_sql, dealership_data)
        dealership_ids.append(cur.fetchone()[0])
    
    logger.info(f"Inserted {len(dealership_ids)} dealerships")
    return dealership_ids

# Insert data into customers table
def insert_customers(cur, dealership_ids):
    logger.info("Inserting data into customers table...")
    customers_sql = """
        INSERT INTO customers (first_name, last_name, email, phone, address, city, country, 
                              date_of_birth, registration_date, loyalty_points, preferred_dealership_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING customer_id
    """
    customer_ids = []
    
    # Insert at least 50 customers
    for _ in range(100):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        phone = fake.phone_number()
        address = fake.address().replace("\n", ", ")
        city = fake.city()
        country = random.choice([item for sublist in countries.values() for item in sublist])
        
        # Generate ages mostly 35-65 for realistic Porsche demographics
        age = int(np.random.normal(50, 10))
        age = max(25, min(80, age))  # Clamp between 25 and 80
        date_of_birth = datetime.now() - timedelta(days=365*age)
        
        # Registration date within the last 10 years
        registration_date = fake.date_between(start_date='-10y', end_date='today')
        
        # Loyalty points - higher for longer-term customers
        days_registered = (datetime.now().date() - registration_date).days
        loyalty_base = days_registered / 30  # roughly months
        loyalty_points = int(loyalty_base * random.uniform(0.8, 1.5))
        
        preferred_dealership_id = random.choice(dealership_ids)
        
        customer_data = (first_name, last_name, email, phone, address, city, country,
                         date_of_birth, registration_date, loyalty_points, preferred_dealership_id)
        
        cur.execute(customers_sql, customer_data)
        customer_ids.append(cur.fetchone()[0])
    
    logger.info(f"Inserted {len(customer_ids)} customers")
    return customer_ids

# Insert data into sales table
def insert_sales(cur, customer_ids, dealership_ids, model_ids):
    logger.info("Inserting data into sales table...")
    sales_sql = """
        INSERT INTO sales (customer_id, dealership_id, model_id, sale_date, price, payment_method,
                          currency, customization_cost, vin, color, options, warranty_years)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING sale_id, vin
    """
    
    # Generate unique VINs
    vins = generate_vins(200)
    sale_records = []
    
    # Porsche colors
    colors = ['Carrara White', 'Jet Black', 'Guards Red', 'Racing Yellow', 'GT Silver', 
              'Gentian Blue', 'Agate Grey', 'Chalk', 'Miami Blue', 'Lava Orange', 
              'Crayon', 'Night Blue', 'Mamba Green']
    
    # Payment methods
    payment_methods = ['Financing', 'Cash', 'Lease']
    
    # Common options
    option_packages = [
        'Sport Chrono Package', 'Premium Package', 'Sport Design Package',
        'Adaptive Sport Seats', 'Panoramic Roof', 'Burmester Sound System',
        'Ceramic Composite Brakes', 'Adaptive Cruise Control', 'Lane Change Assist',
        'Surround View Camera', 'Night Vision Assist', 'Carbon Fiber Interior'
    ]
    
    # Generate sales data
    for i in range(200):
        customer_id = random.choice(customer_ids)
        dealership_id = random.choice(dealership_ids)
        
        # Models have different popularity
        if random.random() < 0.6:
            # More popular models (911, Cayenne, Taycan)
            model_id = model_ids[random.choice([0, 1, 2, 4, 8])]
        else:
            model_id = random.choice(model_ids)
        
        # Sales date - more recent years have more sales (growing trend)
        year_weights = [0.05, 0.1, 0.15, 0.2, 0.5]  # Last year has 50% of sales
        years_ago = random.choices(range(5), weights=year_weights)[0]
        sale_date = fake.date_between(start_date=f'-{years_ago+1}y', end_date=f'-{years_ago}y')
        
        # Price includes base price plus customization
        base_price = random.uniform(60000, 200000)  # Base price varies by model
        customization_cost = random.uniform(0, 50000) if random.random() < 0.7 else 0
        price = base_price + customization_cost
        
        payment_method = random.choice(payment_methods)
        currency = 'USD'  # Default to USD
        
        # Higher-end models get more customization
        if price > 150000:
            num_options = random.randint(3, 8)
        else:
            num_options = random.randint(0, 4)
        
        options = ', '.join(random.sample(option_packages, num_options))
        color = random.choice(colors)
        
        # Warranty years - higher for more expensive cars
        if price > 180000:
            warranty_years = random.choice([3, 4, 5])
        else:
            warranty_years = random.choice([2, 3])
        
        vin = vins.pop()
        
        sale_data = (customer_id, dealership_id, model_id, sale_date, price, payment_method,
                    currency, customization_cost, vin, color, options, warranty_years)
        
        cur.execute(sales_sql, sale_data)
        result = cur.fetchone()
        sale_records.append((result[0], result[1]))  # sale_id, vin
    
    logger.info(f"Inserted {len(sale_records)} sales")
    return sale_records

# Insert data into service_records table
def insert_service_records(cur, sale_records, dealership_ids):
    logger.info("Inserting data into service_records table...")
    service_sql = """
        INSERT INTO service_records (vin, dealership_id, service_date, mileage, service_type,
                                    description, cost, technician, parts_replaced, hours_spent,
                                    customer_satisfaction)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    # Service types and their typical costs
    service_types = {
        'Regular Maintenance': (500, 1500),
        'Oil Change': (200, 400),
        'Brake Service': (800, 2000),
        'Tire Replacement': (1200, 3000),
        'Engine Repair': (2000, 8000),
        'Transmission Service': (1500, 4000),
        'Electrical System': (800, 3000),
        'Body Work': (1500, 10000),
        'Interior Repair': (500, 2000),
        'Performance Upgrade': (3000, 15000)
    }
    
    # Parts that might be replaced
    parts = [
        'Air Filter', 'Oil Filter', 'Brake Pads', 'Brake Rotors',
        'Tires', 'Battery', 'Spark Plugs', 'Fuel Pump', 'Water Pump',
        'Alternator', 'Timing Belt', 'Transmission Fluid', 'Coolant',
        'Suspension Components', 'Exhaust System'
    ]
    
    # Technician names
    technicians = [fake.name() + " (" + random.choice(["Master", "Senior", "Junior", "Certified"]) + ")" 
                   for _ in range(20)]
    
    # Generate service records
    service_count = 0
    for sale_id, vin in sale_records:
        # Each car might have multiple service visits
        num_services = random.choices([0, 1, 2, 3, 4, 5], weights=[0.1, 0.2, 0.3, 0.2, 0.1, 0.1])[0]
        
        for s in range(num_services):
            # Service typically happens some time after purchase
            days_after_purchase = random.randint(30, 1500)
            service_date = fake.date_between(start_date=f'+{days_after_purchase}d', end_date=f'+{days_after_purchase+500}d')
            
            # Usually serviced at the selling dealership, but sometimes elsewhere
            if random.random() < 0.7:
                dealership_id = random.choice(dealership_ids)
            else:
                dealership_id = random.choice(dealership_ids)
            
            # Mileage increases with time
            base_mileage = days_after_purchase * 0.4  # Average 40 miles per day
            mileage = int(base_mileage * random.uniform(0.7, 1.3))  # Some variation
            
            # Select service type and cost
            service_type = random.choice(list(service_types.keys()))
            min_cost, max_cost = service_types[service_type]
            cost = random.uniform(min_cost, max_cost)
            
            # Description
            description = f"{service_type} - {fake.sentence()}"
            
            # Parts replaced (0-3 items)
            num_parts = random.randint(0, 3)
            parts_replaced = ', '.join(random.sample(parts, num_parts)) if num_parts > 0 else None
            
            # Hours spent depends on service type
            if service_type in ['Regular Maintenance', 'Oil Change']:
                hours_spent = random.uniform(0.5, 2.5)
            elif service_type in ['Brake Service', 'Tire Replacement', 'Electrical System', 'Interior Repair']:
                hours_spent = random.uniform(1.5, 4)
            else:
                hours_spent = random.uniform(3, 12)
            
            # Customer satisfaction - generally high but some variations
            satisfaction_weights = [0.01, 0.04, 0.15, 0.3, 0.5]  # Weighted towards 4-5 stars
            customer_satisfaction = random.choices(range(1, 6), weights=satisfaction_weights)[0]
            
            service_data = (vin, dealership_id, service_date, mileage, service_type, description,
                           cost, random.choice(technicians), parts_replaced, hours_spent, customer_satisfaction)
            
            cur.execute(service_sql, service_data)
            service_count += 1
            
    logger.info(f"Inserted {service_count} service records")

def main():
    """Main function to populate the database with sample data"""
    conn = None
    try:
        # Connect to the database
        logger.info("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**db_params)
        conn.autocommit = False
        cur = conn.cursor()
        
        # Insert data into tables
        model_ids = insert_models(cur)
        dealership_ids = insert_dealerships(cur)
        customer_ids = insert_customers(cur, dealership_ids)
        sale_records = insert_sales(cur, customer_ids, dealership_ids, model_ids)
        insert_service_records(cur, sale_records, dealership_ids)
        
        # Commit the changes
        conn.commit()
        logger.info("Data generation completed successfully")
        
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Error: {error}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    main()
