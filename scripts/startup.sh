#!/bin/bash

echo "Starting Environment Setup..."

echo "Creating SQLite database with data..."
python scripts/setup_langchain_db.py

echo "Creating sample JIRA tickets..."
# python scripts/create_jira_tickets.py

echo "Setup complete! You can now run the data analysis agent."
