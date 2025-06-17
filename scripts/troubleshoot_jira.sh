#!/bin/bash

echo "JIRA Troubleshooting Script"
echo "============================"
echo

# Check if JIRA container is running
echo "Checking if JIRA container is running..."
JIRA_RUNNING=$(docker ps | grep jira_server | wc -l)

if [ $JIRA_RUNNING -eq 0 ]; then
  echo "❌ JIRA container is not running!"
  echo "Try starting it with: docker-compose up -d jira"
  exit 1
else
  echo "✅ JIRA container is running"
fi

# Check container logs for common issues
echo
echo "Checking JIRA logs for common issues..."
SETUP_COMPLETE=$(docker logs jira_server 2>&1 | grep "Jira startup complete" | wc -l)
DB_ERROR=$(docker logs jira_server 2>&1 | grep "Database connection failed" | wc -l)

if [ $SETUP_COMPLETE -gt 0 ]; then
  echo "✅ JIRA startup completed successfully"
else
  echo "❌ JIRA might still be starting up"
  echo "Wait a few more minutes and try again."
fi

if [ $DB_ERROR -gt 0 ]; then
  echo "❌ Database connection issues detected!"
  echo "Make sure the database settings in your .env file are correct."
fi

# Display JIRA access information
echo
echo "JIRA access information:"
echo "-------------------------"
echo "URL: http://localhost:8080"
echo "Default credentials: admin/admin"
echo
echo "If you cannot log in, you may need to:"
echo "1. Complete the initial setup wizard first"
echo "2. Make sure the jiradb database was created successfully"
echo "3. Reset the container: docker-compose down && docker-compose up -d"
echo
echo "For more detailed logs, run: docker logs jira_server"
