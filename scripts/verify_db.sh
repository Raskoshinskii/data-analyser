#!/bin/bash

echo "Database Connection Verification Script"
echo "======================================"

# Load environment variables
source .env

# Check if PostgreSQL container is running
echo "Checking PostgreSQL container..."
PG_RUNNING=$(docker ps | grep porsche_db | wc -l)

if [ $PG_RUNNING -eq 0 ]; then
  echo "❌ PostgreSQL container is not running!"
  exit 1
else
  echo "✅ PostgreSQL container is running"
fi

# Verify main database
echo "Verifying main database (${POSTGRES_DB})..."
docker exec porsche_db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "SELECT 1" >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Successfully connected to ${POSTGRES_DB} database"
else
  echo "❌ Failed to connect to ${POSTGRES_DB} database"
fi

# Verify JIRA database
echo "Verifying JIRA database (${JIRA_DB_NAME})..."
docker exec porsche_db psql -U ${POSTGRES_USER} -d ${JIRA_DB_NAME} -c "SELECT 1" >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Successfully connected to ${JIRA_DB_NAME} database"
else
  echo "❌ Failed to connect to ${JIRA_DB_NAME} database"
  echo "Attempting to create JIRA database manually..."
  docker exec porsche_db psql -U ${POSTGRES_USER} -c "CREATE DATABASE ${JIRA_DB_NAME};"
  docker exec porsche_db psql -U ${POSTGRES_USER} -c "GRANT ALL PRIVILEGES ON DATABASE ${JIRA_DB_NAME} TO ${POSTGRES_USER};"
  echo "Database creation attempted. Verifying again..."
  docker exec porsche_db psql -U ${POSTGRES_USER} -d ${JIRA_DB_NAME} -c "SELECT 1" >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo "✅ Successfully created and connected to ${JIRA_DB_NAME} database"
  else
    echo "❌ Failed to create ${JIRA_DB_NAME} database"
  fi
fi

echo -e "\nNext steps:"
echo "1. Restart JIRA: docker-compose restart jira"
echo "2. Visit http://localhost:8080 and complete the setup wizard"
echo "3. Use the following database settings in JIRA setup:"
echo "   - Database type: PostgreSQL"
echo "   - Hostname: postgres (not localhost)"
echo "   - Port: 5432"
echo "   - Database: ${JIRA_DB_NAME}"
echo "   - Username: ${POSTGRES_USER}"
echo "   - Password: ${POSTGRES_PASSWORD}"
