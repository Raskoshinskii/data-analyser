# 🤖 Data Analysis Automation Agent

An intelligent automation system that processes data analysis requests, generates appropriate SQL queries, executes them against a database, and delivers business insights.

## 🌟 Features

- 📊 Automated SQL generation from natural language requests
- ✅ SQL validation for safety and correctness
- 🔍 Intelligent data analysis and insight generation
- 🛡️ Error handling and retry mechanisms

## 🚀 Getting Started

### Prerequisites

- 🐍 Python 3.11+
- 🐘 PostgreSQL database
- 🔑 OpenAI API key
- 🐋 Docker and Docker Compose (for local development)

### 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/data-analyzer.git
cd data-analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

1. Set up the `.env` file in the project root:
```
OPENAI_API_KEY=your_api_key_here
```

2. Update the configuration in `config/config.yaml`:
```yaml
database:
  connection_string: "postgresql://username:password@host:port/database"
```

## 🏁 Usage

### Using the Mock Environment for Development

This project includes a self-contained development environment with mock data:

1. Make the scripts executable:
```bash
chmod +x scripts/make_executable.sh
./scripts/make_executable.sh
```

2. Install mock data requirements:
```bash
python scripts/install_mock_requirements.py
```

3. Start the Docker development environment:
```bash
./scripts/startup.sh
```

This will:
- Start a PostgreSQL Docker container
- Create a sample database schema
- Populate it with Porsche-related mock data

4. Verify the database is setup correctly:
```bash
./scripts/verify_db.sh
```

### Running the Agent

Run the agent using one of the following commands:

```bash
# Process a data analysis request
python main.py --query "Analyze the sales performance of different Porsche models during Q1 2023"

# Use a specific configuration file
python main.py --config config/docker-config.yaml --query "Compare dealership performance across regions"
```

### Common Command Line Options

- `--config`: Path to a config file (defaults to `config/config.yaml`)
- `--query`: The data analysis query to process

## 🔄 Workflow 

The agent follows this workflow:

1. **Task Understanding**: Interprets the natural language query
2. **SQL Generation**: Creates an SQL query that fulfills the request
3. **Query Validation**: Validates the query for syntax, safety, and semantic correctness
4. **Query Execution**: Runs the validated query against the database
5. **Results Validation**: Ensures the results are reasonable for the task
6. **Insight Generation**: Analyzes the results to create business insights

## 📊 Database Schema

The sample database contains tables for:
- `models` - Porsche car models information
- `dealerships` - Dealership locations and details
- `customers` - Customer demographic information
- `sales` - Vehicle sales records
- `service_records` - Vehicle service and maintenance history

## 🔍 Troubleshooting

- **Database Errors**: Check your database connection string and ensure the database is running
- **OpenAI API Errors**: Ensure your API key is correctly set in the .env file
- **Agent Failures**: Check the logs in `data_analyzer.log` for detailed error information
# Check JIRA logs
docker logs jira_server
```

### Running the Agent

Run the agent using one of the following commands:

```bash
# Process all open tickets (up to default limit)
python main.py

# Process a specific ticket
python main.py --ticket DATA-123

# Process multiple tickets with a specific limit
python main.py --max-tickets 10

# Use a specific configuration file
python main.py --config config/docker-config.yaml
```

### Common Command Line Options

- `--config`: Path to a config file (defaults to `config/config.yaml`)
- `--ticket`: Process a specific JIRA ticket ID
- `--max-tickets`: Maximum number of tickets to process (defaults to 5)

## 🔄 Workflow 

The agent follows this workflow:

1. **Ticket Extraction**: Retrieves data analysis requests from JIRA tickets
2. **Task Understanding**: Extracts the task description from the ticket
3. **SQL Generation**: Creates an SQL query that fulfills the request
4. **Query Validation**: Validates the query for syntax, safety, and semantic correctness
5. **Query Execution**: Runs the validated query against the database
6. **Results Validation**: Ensures the results are reasonable for the task
7. **Insight Generation**: Analyzes the results to create business insights
8. **Ticket Update**: Updates the JIRA ticket with findings and marks it as resolved

## 📝 JIRA Ticket Requirements

For a ticket to be processed by the agent, it should:

1. Be in the configured JIRA project
2. Have the label `data_analysis`
3. Be in the "Open" status
4. Contain a clear description of the data analysis task

Example ticket description:
```
Please analyze the sales performance of different Porsche models during Q1 2023.
Compare with previous quarters and identify top-performing models and any emerging trends.
```

## 📊 Database Schema

The sample database contains tables for:
- `models` - Porsche car models information
- `dealerships` - Dealership locations and details
- `customers` - Customer demographic information
- `sales` - Vehicle sales records
- `service_records` - Vehicle service and maintenance history

## 🔍 Troubleshooting

- **JIRA Connection Issues**: Verify your JIRA credentials and URL in the config file
- **Database Errors**: Check your database connection string and ensure the database is running
- **OpenAI API Errors**: Ensure your API key is correctly set in the .env file
- **Agent Failures**: Check the logs in `data_analyzer.log` for detailed error information

