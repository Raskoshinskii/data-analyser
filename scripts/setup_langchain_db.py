import logging
import os
import sqlite3
from langchain.sql_database import SQLDatabase
from langchain_community.utilities import SQLDatabase as SQLDatabaseCommunity

# set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# database path
DB_PATH = os.path.expanduser("./data/porsche_analytics.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# car models data
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

# dealership data
dealerships = [
    ('Porsche New York City', '711 11th Avenue, New York, NY 10019', 'New York', 'United States', 'North America', '2000-03-15', True, 30, 4.7, 'John Smith'),
    ('Porsche Berlin', 'Franklinstrasse 23, 10587 Berlin', 'Berlin', 'Germany', 'Europe', '1998-06-20', True, 25, 4.8, 'Hans Mueller'),
    ('Porsche Los Angeles', '8425 Wilshire Blvd, Beverly Hills, CA 90211', 'Los Angeles', 'United States', 'North America', '1999-11-10', True, 35, 4.6, 'David Johnson'),
    ('Porsche Tokyo', '2-chōme-6-15 Roppongi, Minato City, Tokyo', 'Tokyo', 'Japan', 'Asia Pacific', '2005-04-30', True, 20, 4.9, 'Takeshi Tanaka'),
    ('Porsche London', '27 Berkeley Square, Mayfair, London W1J 6DS', 'London', 'United Kingdom', 'Europe', '1997-09-12', True, 22, 4.5, 'Emma Wilson'),
    ('Porsche Dubai', 'Sheikh Zayed Rd, Dubai', 'Dubai', 'United Arab Emirates', 'Middle East', '2010-01-18', True, 40, 4.8, 'Ahmed Al-Farsi'),
    ('Porsche Melbourne', '121 Swan St, Richmond VIC 3121', 'Melbourne', 'Australia', 'Asia Pacific', '2008-07-22', True, 18, 4.6, 'Sarah Johnson'),
    ('Porsche Munich', 'Olof-Palme-Straße 35, 81829 München', 'Munich', 'Germany', 'Europe', '1992-05-05', True, 30, 4.7, 'Franz Weber'),
    ('Porsche Shanghai', '888 Tianshan Road, Shanghai', 'Shanghai', 'China', 'Asia Pacific', '2012-11-28', True, 25, 4.4, 'Li Wei'),
    ('Porsche Paris', '73 Avenue des Champs-Élysées, 75008 Paris', 'Paris', 'France', 'Europe', '1994-02-14', True, 20, 4.5, 'Claire Dubois')
]

# customer data
customers = [
    ('Michael', 'Johnson', 'michael.j@example.com', '555-1234', '123 Park Avenue, New York, NY', 'New York', 'United States', '1975-06-15', '2015-03-10', 350, 1),
    ('Emma', 'Schmidt', 'emma.s@example.com', '555-2345', 'Münchener Str. 45, Berlin', 'Berlin', 'Germany', '1982-11-23', '2016-07-22', 280, 2),
    ('James', 'Williams', 'j.williams@example.com', '555-3456', '789 Beverly Blvd, Los Angeles, CA', 'Los Angeles', 'United States', '1968-04-30', '2012-12-05', 520, 3),
    ('Yuki', 'Tanaka', 'yuki.t@example.com', '555-4567', '4-2-1 Roppongi, Minato-ku, Tokyo', 'Tokyo', 'Japan', '1979-08-17', '2018-01-15', 190, 4),
    ('Oliver', 'Taylor', 'oliver.t@example.com', '555-5678', '25 Oxford Street, London', 'London', 'United Kingdom', '1984-03-12', '2017-10-08', 220, 5),
    ('Fatima', 'Al-Sayed', 'fatima.a@example.com', '555-6789', 'Palm Jumeirah, Dubai', 'Dubai', 'United Arab Emirates', '1988-07-05', '2019-04-20', 120, 6),
    ('Robert', 'Chen', 'robert.c@example.com', '555-7890', '45 Collins Street, Melbourne', 'Melbourne', 'Australia', '1972-09-28', '2014-08-17', 380, 7),
    ('Sophia', 'Wagner', 'sophia.w@example.com', '555-8901', 'Maximilianstrasse 15, Munich', 'Munich', 'Germany', '1981-12-03', '2013-05-22', 420, 8),
    ('Wei', 'Zhang', 'wei.z@example.com', '555-9012', '123 Nanjing Road, Shanghai', 'Shanghai', 'China', '1976-02-18', '2020-03-10', 90, 9),
    ('Antoine', 'Dubois', 'antoine.d@example.com', '555-0123', '42 Rue de Rivoli, Paris', 'Paris', 'France', '1970-10-25', '2011-11-30', 580, 10)
]

# sales data
sales = [
    (1, 1, 1, '2022-03-15', 110500.00, 'Financing', 'USD', 9300.00, 'WP0AA2A91NS227619', 'Carrara White', 'Sport Chrono Package, Premium Package', 3),
    (2, 2, 3, '2022-05-22', 92400.00, 'Cash', 'EUR', 5700.00, 'WP0BA2Y65PS275831', 'Jet Black', 'Panoramic Roof, Burmester Sound System', 3),
    (3, 3, 2, '2022-06-10', 215000.00, 'Financing', 'USD', 8000.00, 'WP0CD2Y62PS130172', 'Guards Red', 'Sport Chrono Package, Ceramic Composite Brakes', 4),
    (4, 4, 9, '2022-07-05', 98500.00, 'Lease', 'JPY', 4900.00, 'WP0AA2A71NS241053', 'Miami Blue', 'Premium Package, Sport Design Package', 2),
    (5, 5, 5, '2022-08-17', 72500.00, 'Financing', 'GBP', 3500.00, 'WP0AB2A90NS267314', 'Gentian Blue', 'Adaptive Sport Seats, Lane Change Assist', 3),
    (6, 6, 4, '2022-09-22', 182000.00, 'Cash', 'AED', 12000.00, 'WP0CD2Y68PS153047', 'GT Silver', 'Sport Chrono Package, Night Vision Assist', 5),
    (7, 7, 7, '2022-10-14', 65000.00, 'Financing', 'AUD', 5000.00, 'WP0AA2A77NS219845', 'Chalk', 'Burmester Sound System, Sport Design Package', 3),
    (8, 8, 11, '2022-11-30', 167500.00, 'Lease', 'EUR', 6500.00, 'WP0AB2A96NS285621', 'Lava Orange', 'Carbon Fiber Interior, Ceramic Composite Brakes', 4),
    (9, 9, 6, '2022-12-12', 59800.00, 'Cash', 'CNY', 5200.00, 'WP0AA2A73NS253197', 'Mamba Green', 'Premium Package, Adaptive Cruise Control', 2),
    (10, 10, 10, '2023-01-25', 79900.00, 'Financing', 'EUR', 7800.00, 'WP0BA2Y61PS291358', 'Crayon', 'Panoramic Roof, Surround View Camera', 3)
]

# service records
service_records = [
    ('WP0AA2A91NS227619', 1, '2022-09-20', 5000, 'Regular Maintenance', 'Oil change and standard service', 850.00, 'James Wilson (Master)', 'Oil Filter, Air Filter', 2.5, 5),
    ('WP0BA2Y65PS275831', 2, '2022-11-15', 8000, 'Brake Service', 'Front brake pad replacement and inspection', 1200.00, 'Erik Schmidt (Senior)', 'Brake Pads', 3.0, 5),
    ('WP0CD2Y62PS130172', 3, '2023-01-10', 7500, 'Regular Maintenance', '7,500 mile service and software update', 950.00, 'Michael Brown (Master)', 'Oil Filter, Cabin Filter', 2.0, 4),
    ('WP0AA2A71NS241053', 4, '2023-02-05', 10000, 'Tire Replacement', 'All four tires replaced due to wear', 2800.00, 'Kenji Nakamura (Certified)', 'Tires', 2.0, 5),
    ('WP0AB2A90NS267314', 5, '2023-03-22', 15000, 'Regular Maintenance', '15,000 mile comprehensive service', 1450.00, 'Robert Johnson (Senior)', 'Oil Filter, Air Filter, Spark Plugs', 3.5, 4),
    ('WP0CD2Y68PS153047', 6, '2023-04-17', 5000, 'Electrical System', 'Infotainment system troubleshooting and update', 950.00, 'Mohammed Al-Faisal (Master)', 'None', 1.5, 3),
    ('WP0AA2A77NS219845', 7, '2023-05-10', 12000, 'Performance Upgrade', 'Sport exhaust system installation', 3800.00, 'David Thompson (Senior)', 'Exhaust System', 6.0, 5),
    ('WP0AB2A96NS285621', 8, '2023-06-25', 9000, 'Regular Maintenance', 'Oil change and brake fluid flush', 1100.00, 'Hans Weber (Master)', 'Oil Filter, Brake Fluid', 2.5, 5),
    ('WP0AA2A73NS253197', 9, '2023-07-15', 6000, 'Interior Repair', 'Center console replacement due to wear', 1200.00, 'Li Jie (Certified)', 'Center Console Components', 4.0, 4),
    ('WP0BA2Y61PS291358', 10, '2023-08-28', 10000, 'Regular Maintenance', '10,000 mile service and alignment', 1350.00, 'Pierre Dubois (Master)', 'Oil Filter, Cabin Filter', 3.0, 5)
]

# tables creation (SQLite based!)
create_tables_sql = """
-- Models table - information about Porsche car models
CREATE TABLE models (
    model_id INTEGER PRIMARY KEY,
    model_name TEXT NOT NULL,
    model_code TEXT NOT NULL,
    production_start_year INTEGER,
    production_end_year INTEGER,
    segment TEXT,
    base_price REAL,
    horsepower INTEGER,
    body_type TEXT,
    is_electric INTEGER DEFAULT 0,
    description TEXT
);

-- Dealerships table - Porsche dealerships information
CREATE TABLE dealerships (
    dealership_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    city TEXT,
    country TEXT,
    region TEXT,
    opening_date TEXT,
    service_center INTEGER DEFAULT 1,
    sales_capacity INTEGER,
    rating REAL,
    manager_name TEXT
);

-- Customers table - Customer information
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    city TEXT,
    country TEXT,
    date_of_birth TEXT,
    registration_date TEXT,
    loyalty_points INTEGER DEFAULT 0,
    preferred_dealership_id INTEGER REFERENCES dealerships(dealership_id)
);

-- Sales table - Vehicle sales records
CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    dealership_id INTEGER REFERENCES dealerships(dealership_id),
    model_id INTEGER REFERENCES models(model_id),
    sale_date TEXT NOT NULL,
    price REAL NOT NULL,
    payment_method TEXT,
    currency TEXT DEFAULT 'USD',
    customization_cost REAL DEFAULT 0,
    vin TEXT UNIQUE,
    color TEXT,
    options TEXT,
    warranty_years INTEGER DEFAULT 2
);

-- Service records table - Maintenance and service data
CREATE TABLE service_records (
    service_id INTEGER PRIMARY KEY,
    vin TEXT REFERENCES sales(vin),
    dealership_id INTEGER REFERENCES dealerships(dealership_id),
    service_date TEXT NOT NULL,
    mileage INTEGER,
    service_type TEXT,
    description TEXT,
    cost REAL,
    technician TEXT,
    parts_replaced TEXT,
    hours_spent REAL,
    customer_satisfaction INTEGER CHECK (customer_satisfaction BETWEEN 1 AND 5)
);
"""

def create_langchain_db():
    """Create the SQLite database and tables"""
    # remove existing database if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        logger.info(f"Removed existing database at {DB_PATH}")
    
    # connect to SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # creae tables
    logger.info("Creating database tables...")
    cursor.executescript(create_tables_sql)
    conn.commit()
    
    # insert data
    logger.info("Inserting model data...")
    cursor.executemany("""
        INSERT INTO models (
            model_name, model_code, production_start_year, production_end_year,
            segment, base_price, horsepower, body_type, is_electric, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, porsche_models)
    
    logger.info("Inserting dealership data...")
    cursor.executemany("""
        INSERT INTO dealerships (
            name, address, city, country, region, opening_date, service_center, sales_capacity, rating, manager_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, dealerships)
    
    logger.info("Inserting customer data...")
    cursor.executemany("""
        INSERT INTO customers (
            first_name, last_name, email, phone, address, city, country, date_of_birth, registration_date, loyalty_points, preferred_dealership_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, customers)
    
    logger.info("Inserting sales data...")
    cursor.executemany("""
        INSERT INTO sales (
            customer_id, dealership_id, model_id, sale_date, price, payment_method, currency, customization_cost, vin, color, options, warranty_years
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sales)
    
    logger.info("Inserting service records...")
    cursor.executemany("""
        INSERT INTO service_records (
            vin, dealership_id, service_date, mileage, service_type, description,
            cost, technician, parts_replaced, hours_spent, customer_satisfaction
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, service_records)
    
    conn.commit()
    conn.close()
    
    logger.info(f"Database created successfully at {DB_PATH}")
    
    # test connection to created DB using LangChain 
    try:
        try:
            db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
            logger.info("Successfully connected to database with LangChain")
        except:
            db = SQLDatabaseCommunity.from_uri(f"sqlite:///{DB_PATH}")
            logger.info("Successfully connected to database with LangChain (community version)")
        
        tables = db.get_usable_table_names()
        logger.info(f"Available tables: {tables}")
        
        return db
    except Exception as e:
        logger.error(f"Error connecting to database with LangChain: {e}")
        return None

if __name__ == "__main__":
    logger.info("Starting database setup process...")
    db = create_langchain_db()
    logger.info("Database setup complete!")
