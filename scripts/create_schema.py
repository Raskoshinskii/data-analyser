import psycopg2
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Database connection parameters
db_params = {
    'dbname': 'porsche_analytics',
    'user': 'porsche_admin',
    'password': 'p0rsch3_secret',
    'host': 'localhost',
    'port': '5432'
}

# SQL statements to create tables
create_tables_sql = """
-- Models table - information about Porsche car models
CREATE TABLE models (
    model_id SERIAL PRIMARY KEY,
    model_name VARCHAR(50) NOT NULL,
    model_code VARCHAR(20) NOT NULL,
    production_start_year INTEGER,
    production_end_year INTEGER,
    segment VARCHAR(20),
    base_price NUMERIC(12, 2),
    horsepower INTEGER,
    body_type VARCHAR(30),
    is_electric BOOLEAN DEFAULT FALSE,
    description TEXT
);

-- Dealerships table - Porsche dealerships information
CREATE TABLE dealerships (
    dealership_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    city VARCHAR(50),
    country VARCHAR(50),
    region VARCHAR(50),
    opening_date DATE,
    service_center BOOLEAN DEFAULT TRUE,
    sales_capacity INTEGER,
    rating DECIMAL(3, 2),
    manager_name VARCHAR(100)
);

-- Customers table - Customer information
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    country VARCHAR(50),
    date_of_birth DATE,
    registration_date DATE,
    loyalty_points INTEGER DEFAULT 0,
    preferred_dealership_id INTEGER REFERENCES dealerships(dealership_id)
);

-- Sales table - Vehicle sales records
CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    dealership_id INTEGER REFERENCES dealerships(dealership_id),
    model_id INTEGER REFERENCES models(model_id),
    sale_date DATE NOT NULL,
    price NUMERIC(12, 2) NOT NULL,
    payment_method VARCHAR(20),
    currency VARCHAR(3) DEFAULT 'USD',
    customization_cost NUMERIC(10, 2) DEFAULT 0,
    vin VARCHAR(17) UNIQUE,
    color VARCHAR(30),
    options TEXT,
    warranty_years INTEGER DEFAULT 2
);

-- Service records table - Maintenance and service data
CREATE TABLE service_records (
    service_id SERIAL PRIMARY KEY,
    vin VARCHAR(17) REFERENCES sales(vin),
    dealership_id INTEGER REFERENCES dealerships(dealership_id),
    service_date DATE NOT NULL,
    mileage INTEGER,
    service_type VARCHAR(50),
    description TEXT,
    cost NUMERIC(10, 2),
    technician VARCHAR(100),
    parts_replaced TEXT,
    hours_spent DECIMAL(5, 2),
    customer_satisfaction INTEGER CHECK (customer_satisfaction BETWEEN 1 AND 5)
);
"""

def create_schema():
    """Create the database schema for Porsche analytics"""
    conn = None
    try:
        # Connect to the database
        logger.info("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        
        # Execute the create tables SQL
        logger.info("Creating tables...")
        cur.execute(create_tables_sql)
        
        # Commit the changes
        conn.commit()
        logger.info("Schema created successfully")
        
        # Close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Error: {error}")
    finally:
        if conn is not None:
            conn.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    create_schema()
