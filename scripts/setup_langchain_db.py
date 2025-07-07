import logging
import os
import sqlite3

from langchain.sql_database import SQLDatabase
from langchain_community.utilities import SQLDatabase as SQLDatabaseCommunity
from constants import (
    TABLES_CREATION_SQL,
    PORSCHE_MODELS_DATA,
    DEALERSHIP_DATA,
    CUSTOMERS_DATA,
    SALES_DATA,
    SERVICE_RECORDS_DATA,
)

# set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# database path
DB_PATH = os.path.expanduser("./data/porsche_analytics.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


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
    cursor.executescript(TABLES_CREATION_SQL)
    conn.commit()

    # insert data
    logger.info("Inserting model data...")
    cursor.executemany(
        """
        INSERT INTO models (
            model_name, model_code, production_start_year, production_end_year,
            segment, base_price, horsepower, body_type, is_electric, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        PORSCHE_MODELS_DATA,
    )

    logger.info("Inserting dealership data...")
    cursor.executemany(
        """
        INSERT INTO dealerships (
            name, address, city, country, region, opening_date, service_center, sales_capacity, rating, manager_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        DEALERSHIP_DATA,
    )

    logger.info("Inserting customer data...")
    cursor.executemany(
        """
        INSERT INTO customers (
            first_name, last_name, email, phone, address, city, country, date_of_birth, registration_date, loyalty_points, preferred_dealership_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        CUSTOMERS_DATA,
    )

    logger.info("Inserting sales data...")
    cursor.executemany(
        """
        INSERT INTO sales (
            customer_id, dealership_id, model_id, sale_date, price, payment_method, currency, customization_cost, vin, color, options, warranty_years
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        SALES_DATA,
    )

    logger.info("Inserting service records...")
    cursor.executemany(
        """
        INSERT INTO service_records (
            vin, dealership_id, service_date, mileage, service_type, description,
            cost, technician, parts_replaced, hours_spent, customer_satisfaction
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        SERVICE_RECORDS_DATA,
    )

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
            logger.info(
                "Successfully connected to database with LangChain (community version)"
            )

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
