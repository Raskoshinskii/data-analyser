#!/bin/bash

echo "Setting up Data Analysis Agent environment..."

# Make scripts executable
chmod +x scripts/make_executable.sh
chmod +x scripts/startup.sh

echo "Scripts are now executable."
echo ""
echo "To install requirements, run: python scripts/install_mock_requirements.py"
echo "To start the Docker environment, run: ./scripts/startup.sh"
echo ""
echo "For more information, see the README.md file."
