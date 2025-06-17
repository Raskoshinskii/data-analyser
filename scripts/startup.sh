#!/bin/bash

echo "Starting Porsche Data Analysis Environment Setup..."

# Start Docker services
echo "Starting Docker services..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 20

# Create database schema
echo "Creating database schema..."
python scripts/create_schema.py

# Generate mock data
echo "Generating mock data..."
python scripts/generate_data.py

echo "Setup complete! You can now run the data analysis agent."
echo "Postgres is available at: localhost:5432"
echo ""
echo "To run the agent with Docker configuration, use:"
echo "python main.py --config config/docker-config.yaml"
echo "Creating sample JIRA tickets..."
python scripts/create_jira_tickets.py

echo "Setup complete! You can now run the data analysis agent."
echo "JIRA is available at: http://localhost:8080"
echo "Postgres is available at: localhost:5432"
echo ""
echo "To run the agent with Docker configuration, use:"
echo "python main.py --config config/docker-config.yaml"
