import os


JIRA_PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY")

# artificially generated data analysis tickets
TICKETS_TO_TEST = [
    # easy tasks
    {
        "id": 1,
        "project": JIRA_PROJECT_KEY,
        "summary": "Car Models Analysis",
        "description": "How many unqiue car models we have per car category? Sort the results in descending order by models_unq_count!",
        "issuetype": "Task",
        "difficulty": "easy",
        "sql": """
            SELECT
                segment,
                COUNT(DISTINCT model_code) AS models_unq_count
            FROM models
            GROUP BY segment
            ORDER BY models_unq_count DESC
        """
    },
    {
        "id": 2,
        "project": JIRA_PROJECT_KEY,
        "summary": "Dealership Performance by Region Analysis",
        "description": "Analyze the average dealership rating and sales capacity by region. Which regions have the highest performing dealerships? Sort the results by average rating in descending order.",
        "issuetype": "Task",
        "difficulty": "easy",
        "sql": """
            SELECT
                region,
                AVG(rating) AS average_rating,
                AVG(sales_capacity) AS average_sales_capacity
            FROM
                dealerships
            GROUP BY
                region
            ORDER BY
                average_rating DESC;
        """
    },
    {
        "id": 3,
        "project": JIRA_PROJECT_KEY,
        "summary": "Count Electric Models",
        "description": "How many electric car models are available in the database? Sort the results in descending order by electric_model_count.",
        "issuetype": "Task",
        "difficulty": "easy",
        "sql": """
            SELECT COUNT(*) AS electric_model_count
            FROM models
            WHERE is_electric = 1;
        """
    },
    {
        "id": 4,
        "project": JIRA_PROJECT_KEY,
        "summary": "Top Regions by Dealerships",
        "description": "Which regions have the most dealerships? Sort the results in descending order by dealership_count.",
        "issuetype": "Task",
        "difficulty": "easy",
        "sql": """
            SELECT region, COUNT(*) AS dealership_count
            FROM dealerships
            GROUP BY region
            ORDER BY dealership_count DESC;
        """
    },
    {
        "id": 5,
        "project": JIRA_PROJECT_KEY,
        "summary": "Average Sale Price by Region and Model",
        "description": "For each region and car model, calculate the average sale price of all cars sold. Sort the results by average_sale_price in descending order.",
        "issuetype": "Task",
        "difficulty": "easy",
        "sql": """
            SELECT 
                d.region,
                m.model_name,
                AVG(s.price) AS average_sale_price
            FROM sales s
            JOIN dealerships d ON s.dealership_id = d.dealership_id
            JOIN models m ON s.model_id = m.model_id
            GROUP BY d.region, m.model_name
            ORDER BY average_sale_price DESC;
        """
    },
    {
        "id": 6,
        "project": JIRA_PROJECT_KEY,
        "summary": "Sales Count by Payment Method",
        "description": "How many cars were sold using each payment method? Sort the results in descending order by sales_count.",
        "issuetype": "Task",
        "difficulty": "easy",
        "sql": """
            SELECT
                payment_method,
                COUNT(*) AS cars_sold
            FROM sales
            GROUP BY payment_method
            ORDER BY cars_sold DESC;
        """
    },
    # medium tasks
    {
        "id": 7,
        "project": JIRA_PROJECT_KEY,
        "summary": "Popular Models by Region",
        "description": "Which car models are most frequently sold in each region? Sort the results by region and sales_count in descending order.",
        "issuetype": "Task",
        "difficulty": "medium",
        "sql": """
            SELECT
                d.region,
                m.model_name,
                COUNT(*) AS sales_count
            FROM sales s
            JOIN dealerships d ON s.dealership_id = d.dealership_id
            JOIN models m ON s.model_id = m.model_id
            GROUP BY d.region, m.model_name
            ORDER BY d.region, sales_count DESC;
        """
    },
    {
        "id": 8,
        "project": JIRA_PROJECT_KEY,
        "summary": "Revenue by Dealership",
        "description": "Calculate total sales revenue for each dealership. Sort by 'total_revenue' in descending order.",
        "issuetype": "Task",
        "difficulty": "medium",
        "sql": """
            SELECT
                d.name AS dealership_name,
                SUM(s.price) AS total_revenue
            FROM sales s
            JOIN dealerships d ON s.dealership_id = d.dealership_id
            GROUP BY d.dealership_id, d.name
            ORDER BY total_revenue DESC;
        """
    },
    {
        "id": 9,
        "project": JIRA_PROJECT_KEY,
        "summary": "Average Age of Customers per Country",
        "description": "What is the average customer age per country based on date_of_birth? Sort the results by average customer age. Don't use :: since it's SQLite. Sort the result in descending order by 'average_age'.",
        "issuetype": "Task",
        "difficulty": "medium",
        "sql": """
            SELECT
                country,
                AVG((julianday('now') - julianday(date_of_birth)) / 365.25) AS average_age
            FROM customers
            WHERE date_of_birth IS NOT NULL
            GROUP BY country
            ORDER BY average_age DESC;
        """
    },
    {
        "id": 10,
        "project": JIRA_PROJECT_KEY,
        "summary": "Service Cost by Dealership",
        "description": "Calculate the total service cost provided by each dealership. Sort the results by 'total_service_cost' in descending order.",
        "issuetype": "Task",
        "difficulty": "medium",
        "sql": """
            SELECT
                dealership_id,
                SUM(cost) AS total_service_cost
            FROM service_records
            GROUP BY dealership_id
            ORDER BY total_service_cost DESC;
        """
    },
    {
        "id": 11,
        "project": JIRA_PROJECT_KEY,
        "summary": "Model Price vs Horsepower",
        "description": "Get average base price and average horsepower for each car body_type. Sort the results by 'body_type' in descending order.",
        "issuetype": "Task",
        "difficulty": "medium",
        "sql": """
            SELECT
                body_type,
                AVG(base_price) AS avg_base_price,
                AVG(horsepower) AS avg_horsepower
            FROM models
            GROUP BY body_type
            ORDER BY body_type DESC;
        """
    },
    # hard tasks
    {
        "id": 12,
        "project": JIRA_PROJECT_KEY,
        "summary": "Top Performing Dealerships",
        "description": "Which dealerships have the highest average rating and highest sales revenue combined? Select top 10 and sort the results by 'combined score' in descending order.",
        "issuetype": "Task",
        "difficulty": "hard",
        "sql": """
            SELECT
                d.dealership_id,
                d.name,
                d.region,
                d.rating AS average_rating,
                COALESCE(SUM(s.price), 0) AS total_sales_revenue,
                d.rating + COALESCE(SUM(s.price), 0) AS combined_score
            FROM dealerships d
            LEFT JOIN sales s ON d.dealership_id = s.dealership_id
            GROUP BY d.dealership_id, d.name, d.region, d.rating
            ORDER BY combined_score DESC
            LIMIT 10;  -- optional, top 10
        """
    },
    {
        "id": 13,
        "project": JIRA_PROJECT_KEY,
        "summary": "Profit Margin by Model",
        "description": "Calculate average profit margin per car model by subtracting base_price from average sale price. Sort the results by 'average_profit_margin' in descending order.",
        "issuetype": "Task",
        "difficulty": "hard",
        "sql": """
            SELECT
                m.model_id,
                m.model_name,
                AVG(s.price) - m.base_price AS average_profit_margin
            FROM models m
            JOIN sales s ON m.model_id = s.model_id
            GROUP BY m.model_id, m.model_name, m.base_price
            ORDER BY average_profit_margin DESC;
        """
    },
    {
        "id": 14,
        "project": JIRA_PROJECT_KEY,
        "summary": "Repeat Customers Analysis",
        "description": "How many customers have purchased more than one car? List their customer IDs and number of purchases. Sort by 'purchase_count' in descending order.",
        "issuetype": "Task",
        "difficulty": "hard",
        "sql": """
            SELECT
                customer_id,
                COUNT(*) AS purchase_count
            FROM sales
            GROUP BY customer_id
            HAVING COUNT(*) > 1
            ORDER BY purchase_count DESC;
        """
    },
    {
        "id": 15,
        "project": JIRA_PROJECT_KEY,
        "summary": "Service Frequency by Model",
        "description": "For each car model, how many service records exist per 10.000 km on average? Sort the results by 'service_records_per_10000_km' in descending order.",
        "issuetype": "Task",
        "difficulty": "hard",
        "sql": """
            SELECT
                s.model_id,
                COUNT(sr.service_id) AS total_service_records,
                SUM(sr.mileage) AS total_mileage,
                (COUNT(sr.service_id) * 10000.0) / NULLIF(SUM(sr.mileage), 0) AS service_records_per_10000_km
            FROM service_records sr
            JOIN sales s ON sr.vin = s.vin
            GROUP BY s.model_id
            ORDER BY service_records_per_10000_km DESC;
        """
    },
    {
        "id": 16,
        "project": JIRA_PROJECT_KEY,
        "summary": "Lifetime Value by Customer",
        "description": "Calculate the lifetime value of each customer based on total purchases and service costs. Sort the results by 'lifetime_value' in descending order. Include only top 10 customers.",
        "issuetype": "Task",
        "difficulty": "hard",
        "sql": """
            SELECT
                c.customer_id,
                COALESCE(SUM(s.price), 0) AS total_purchase_amount,
                COALESCE(SUM(sr.cost), 0) AS total_service_cost,
                COALESCE(SUM(s.price), 0) + COALESCE(SUM(sr.cost), 0) AS lifetime_value
            FROM customers c
            LEFT JOIN sales s ON c.customer_id = s.customer_id
            LEFT JOIN service_records sr ON sr.vin IN (
                SELECT vin FROM sales WHERE customer_id = c.customer_id
            )
            GROUP BY c.customer_id
            ORDER BY lifetime_value DESC
            LIMIT 10;
        """
    },
]

# Database data
PORSCHE_MODELS_DATA = [
    (
        "911 Carrera",
        "P-911-CR",
        1963,
        None,
        "Sports Car",
        101200.00,
        379,
        "Coupe",
        False,
        "Iconic rear-engine sports car",
    ),
    (
        "911 Turbo S",
        "P-911-TS",
        1975,
        None,
        "Sports Car",
        207000.00,
        640,
        "Coupe",
        False,
        "High-performance variant of the 911",
    ),
    (
        "Taycan",
        "P-TAY",
        2019,
        None,
        "Sedan",
        86700.00,
        522,
        "Sedan",
        True,
        "All-electric four-door sports car",
    ),
    (
        "Panamera",
        "P-PAN",
        2009,
        None,
        "Luxury",
        88400.00,
        325,
        "Sedan",
        False,
        "Four-door luxury sports car",
    ),
    (
        "Cayenne",
        "P-CAY",
        2002,
        None,
        "SUV",
        69000.00,
        335,
        "SUV",
        False,
        "Mid-size luxury crossover SUV",
    ),
    (
        "Macan",
        "P-MAC",
        2014,
        None,
        "SUV",
        54900.00,
        248,
        "SUV",
        False,
        "Compact luxury crossover SUV",
    ),
    (
        "718 Boxster",
        "P-BOX",
        1996,
        None,
        "Sports Car",
        62000.00,
        300,
        "Convertible",
        False,
        "Mid-engine two-seater roadster",
    ),
    (
        "718 Cayman",
        "P-CAY",
        2005,
        None,
        "Sports Car",
        60500.00,
        300,
        "Coupe",
        False,
        "Mid-engine two-seater coupe",
    ),
    (
        "Taycan Cross Turismo",
        "P-TAYCT",
        2021,
        None,
        "Wagon",
        93700.00,
        469,
        "Wagon",
        True,
        "All-electric wagon variant of the Taycan",
    ),
    (
        "Cayenne Coupe",
        "P-CAYC",
        2019,
        None,
        "SUV",
        76500.00,
        335,
        "SUV Coupe",
        False,
        "Coupe variant of the Cayenne SUV",
    ),
    (
        "911 GT3",
        "P-911-GT3",
        1999,
        None,
        "Sports Car",
        161100.00,
        502,
        "Coupe",
        False,
        "High-performance variant of the 911",
    ),
    (
        "918 Spyder",
        "P-918",
        2013,
        2015,
        "Hypercar",
        845000.00,
        887,
        "Convertible",
        True,
        "Limited production hybrid sports car",
    ),
    (
        "Carrera GT",
        "P-CGT",
        2003,
        2007,
        "Supercar",
        448000.00,
        605,
        "Convertible",
        False,
        "Mid-engine sports car",
    ),
]

DEALERSHIP_DATA = [
    (
        "Porsche New York City",
        "711 11th Avenue, New York, NY 10019",
        "New York",
        "United States",
        "North America",
        "2000-03-15",
        True,
        30,
        4.7,
        "John Smith",
    ),
    (
        "Porsche Berlin",
        "Franklinstrasse 23, 10587 Berlin",
        "Berlin",
        "Germany",
        "Europe",
        "1998-06-20",
        True,
        25,
        4.8,
        "Hans Mueller",
    ),
    (
        "Porsche Los Angeles",
        "8425 Wilshire Blvd, Beverly Hills, CA 90211",
        "Los Angeles",
        "United States",
        "North America",
        "1999-11-10",
        True,
        35,
        4.6,
        "David Johnson",
    ),
    (
        "Porsche Tokyo",
        "2-chōme-6-15 Roppongi, Minato City, Tokyo",
        "Tokyo",
        "Japan",
        "Asia Pacific",
        "2005-04-30",
        True,
        20,
        4.9,
        "Takeshi Tanaka",
    ),
    (
        "Porsche London",
        "27 Berkeley Square, Mayfair, London W1J 6DS",
        "London",
        "United Kingdom",
        "Europe",
        "1997-09-12",
        True,
        22,
        4.5,
        "Emma Wilson",
    ),
    (
        "Porsche Dubai",
        "Sheikh Zayed Rd, Dubai",
        "Dubai",
        "United Arab Emirates",
        "Middle East",
        "2010-01-18",
        True,
        40,
        4.8,
        "Ahmed Al-Farsi",
    ),
    (
        "Porsche Melbourne",
        "121 Swan St, Richmond VIC 3121",
        "Melbourne",
        "Australia",
        "Asia Pacific",
        "2008-07-22",
        True,
        18,
        4.6,
        "Sarah Johnson",
    ),
    (
        "Porsche Munich",
        "Olof-Palme-Straße 35, 81829 München",
        "Munich",
        "Germany",
        "Europe",
        "1992-05-05",
        True,
        30,
        4.7,
        "Franz Weber",
    ),
    (
        "Porsche Shanghai",
        "888 Tianshan Road, Shanghai",
        "Shanghai",
        "China",
        "Asia Pacific",
        "2012-11-28",
        True,
        25,
        4.4,
        "Li Wei",
    ),
    (
        "Porsche Paris",
        "73 Avenue des Champs-Élysées, 75008 Paris",
        "Paris",
        "France",
        "Europe",
        "1994-02-14",
        True,
        20,
        4.5,
        "Claire Dubois",
    ),
]

CUSTOMERS_DATA = [
    (
        "Michael",
        "Johnson",
        "michael.j@example.com",
        "555-1234",
        "123 Park Avenue, New York, NY",
        "New York",
        "United States",
        "1975-06-15",
        "2015-03-10",
        350,
        1,
    ),
    (
        "Emma",
        "Schmidt",
        "emma.s@example.com",
        "555-2345",
        "Münchener Str. 45, Berlin",
        "Berlin",
        "Germany",
        "1982-11-23",
        "2016-07-22",
        280,
        2,
    ),
    (
        "James",
        "Williams",
        "j.williams@example.com",
        "555-3456",
        "789 Beverly Blvd, Los Angeles, CA",
        "Los Angeles",
        "United States",
        "1968-04-30",
        "2012-12-05",
        520,
        3,
    ),
    (
        "Yuki",
        "Tanaka",
        "yuki.t@example.com",
        "555-4567",
        "4-2-1 Roppongi, Minato-ku, Tokyo",
        "Tokyo",
        "Japan",
        "1979-08-17",
        "2018-01-15",
        190,
        4,
    ),
    (
        "Oliver",
        "Taylor",
        "oliver.t@example.com",
        "555-5678",
        "25 Oxford Street, London",
        "London",
        "United Kingdom",
        "1984-03-12",
        "2017-10-08",
        220,
        5,
    ),
    (
        "Fatima",
        "Al-Sayed",
        "fatima.a@example.com",
        "555-6789",
        "Palm Jumeirah, Dubai",
        "Dubai",
        "United Arab Emirates",
        "1988-07-05",
        "2019-04-20",
        120,
        6,
    ),
    (
        "Robert",
        "Chen",
        "robert.c@example.com",
        "555-7890",
        "45 Collins Street, Melbourne",
        "Melbourne",
        "Australia",
        "1972-09-28",
        "2014-08-17",
        380,
        7,
    ),
    (
        "Sophia",
        "Wagner",
        "sophia.w@example.com",
        "555-8901",
        "Maximilianstrasse 15, Munich",
        "Munich",
        "Germany",
        "1981-12-03",
        "2013-05-22",
        420,
        8,
    ),
    (
        "Wei",
        "Zhang",
        "wei.z@example.com",
        "555-9012",
        "123 Nanjing Road, Shanghai",
        "Shanghai",
        "China",
        "1976-02-18",
        "2020-03-10",
        90,
        9,
    ),
    (
        "Antoine",
        "Dubois",
        "antoine.d@example.com",
        "555-0123",
        "42 Rue de Rivoli, Paris",
        "Paris",
        "France",
        "1970-10-25",
        "2011-11-30",
        580,
        10,
    ),
]

SALES_DATA = [
    (
        1,
        1,
        1,
        "2022-03-15",
        110500.00,
        "Financing",
        "USD",
        9300.00,
        "WP0AA2A91NS227619",
        "Carrara White",
        "Sport Chrono Package, Premium Package",
        3,
    ),
    (
        2,
        2,
        3,
        "2022-05-22",
        92400.00,
        "Cash",
        "EUR",
        5700.00,
        "WP0BA2Y65PS275831",
        "Jet Black",
        "Panoramic Roof, Burmester Sound System",
        3,
    ),
    (
        3,
        3,
        2,
        "2022-06-10",
        215000.00,
        "Financing",
        "USD",
        8000.00,
        "WP0CD2Y62PS130172",
        "Guards Red",
        "Sport Chrono Package, Ceramic Composite Brakes",
        4,
    ),
    (
        4,
        4,
        9,
        "2022-07-05",
        98500.00,
        "Lease",
        "JPY",
        4900.00,
        "WP0AA2A71NS241053",
        "Miami Blue",
        "Premium Package, Sport Design Package",
        2,
    ),
    (
        5,
        5,
        5,
        "2022-08-17",
        72500.00,
        "Financing",
        "GBP",
        3500.00,
        "WP0AB2A90NS267314",
        "Gentian Blue",
        "Adaptive Sport Seats, Lane Change Assist",
        3,
    ),
    (
        6,
        6,
        4,
        "2022-09-22",
        182000.00,
        "Cash",
        "AED",
        12000.00,
        "WP0CD2Y68PS153047",
        "GT Silver",
        "Sport Chrono Package, Night Vision Assist",
        5,
    ),
    (
        7,
        7,
        7,
        "2022-10-14",
        65000.00,
        "Financing",
        "AUD",
        5000.00,
        "WP0AA2A77NS219845",
        "Chalk",
        "Burmester Sound System, Sport Design Package",
        3,
    ),
    (
        8,
        8,
        11,
        "2022-11-30",
        167500.00,
        "Lease",
        "EUR",
        6500.00,
        "WP0AB2A96NS285621",
        "Lava Orange",
        "Carbon Fiber Interior, Ceramic Composite Brakes",
        4,
    ),
    (
        9,
        9,
        6,
        "2022-12-12",
        59800.00,
        "Cash",
        "CNY",
        5200.00,
        "WP0AA2A73NS253197",
        "Mamba Green",
        "Premium Package, Adaptive Cruise Control",
        2,
    ),
    (
        10,
        10,
        10,
        "2023-01-25",
        79900.00,
        "Financing",
        "EUR",
        7800.00,
        "WP0BA2Y61PS291358",
        "Crayon",
        "Panoramic Roof, Surround View Camera",
        3,
    ),
]

SERVICE_RECORDS_DATA = [
    (
        "WP0AA2A91NS227619",
        1,
        "2022-09-20",
        5000,
        "Regular Maintenance",
        "Oil change and standard service",
        850.00,
        "James Wilson (Master)",
        "Oil Filter, Air Filter",
        2.5,
        5,
    ),
    (
        "WP0BA2Y65PS275831",
        2,
        "2022-11-15",
        8000,
        "Brake Service",
        "Front brake pad replacement and inspection",
        1200.00,
        "Erik Schmidt (Senior)",
        "Brake Pads",
        3.0,
        5,
    ),
    (
        "WP0CD2Y62PS130172",
        3,
        "2023-01-10",
        7500,
        "Regular Maintenance",
        "7,500 mile service and software update",
        950.00,
        "Michael Brown (Master)",
        "Oil Filter, Cabin Filter",
        2.0,
        4,
    ),
    (
        "WP0AA2A71NS241053",
        4,
        "2023-02-05",
        10000,
        "Tire Replacement",
        "All four tires replaced due to wear",
        2800.00,
        "Kenji Nakamura (Certified)",
        "Tires",
        2.0,
        5,
    ),
    (
        "WP0AB2A90NS267314",
        5,
        "2023-03-22",
        15000,
        "Regular Maintenance",
        "15,000 mile comprehensive service",
        1450.00,
        "Robert Johnson (Senior)",
        "Oil Filter, Air Filter, Spark Plugs",
        3.5,
        4,
    ),
    (
        "WP0CD2Y68PS153047",
        6,
        "2023-04-17",
        5000,
        "Electrical System",
        "Infotainment system troubleshooting and update",
        950.00,
        "Mohammed Al-Faisal (Master)",
        "None",
        1.5,
        3,
    ),
    (
        "WP0AA2A77NS219845",
        7,
        "2023-05-10",
        12000,
        "Performance Upgrade",
        "Sport exhaust system installation",
        3800.00,
        "David Thompson (Senior)",
        "Exhaust System",
        6.0,
        5,
    ),
    (
        "WP0AB2A96NS285621",
        8,
        "2023-06-25",
        9000,
        "Regular Maintenance",
        "Oil change and brake fluid flush",
        1100.00,
        "Hans Weber (Master)",
        "Oil Filter, Brake Fluid",
        2.5,
        5,
    ),
    (
        "WP0AA2A73NS253197",
        9,
        "2023-07-15",
        6000,
        "Interior Repair",
        "Center console replacement due to wear",
        1200.00,
        "Li Jie (Certified)",
        "Center Console Components",
        4.0,
        4,
    ),
    (
        "WP0BA2Y61PS291358",
        10,
        "2023-08-28",
        10000,
        "Regular Maintenance",
        "10,000 mile service and alignment",
        1350.00,
        "Pierre Dubois (Master)",
        "Oil Filter, Cabin Filter",
        3.0,
        5,
    ),
]

TABLES_CREATION_SQL = create_tables_sql = """
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
