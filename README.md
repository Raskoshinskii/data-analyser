# 🤖 Data Analysis Automation Agent

An intelligent automation system that processes data analysis requests from JIRA tickets, generates appropriate SQL queries, executes them against a database, and delivers business insights.

## 🌟 Features

- 📊 Automated SQL generation from natural language requests
- ✅ SQL validation for safety and correctness
- 🔍 Intelligent data analysis and insight generation
- 🔄 JIRA integration for ticket management
- 🛡️ Error handling and retry mechanisms

## 🚀 Getting Started

### Prerequisites

- 🐍 Python 3.11+
- 🐘 PostgreSQL database
- 🧩 JIRA instance (local or remote)
- 🔑 OpenAI API key

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

1. Create .env file in the project root with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

2. Update the configuration in config/config.yaml:
```yaml
database:
  connection_string: "postgresql://username:password@host:port/database"

jira:
  url: "https://your-company.atlassian.net"
  username: "your_username"
  api_token: "your_api_token"
  project_key: "YOUR_PROJECT"
```

## 🏁 Usage

### Using the Mock Environment for Development

This project includes a self-contained development environment with mock data:

1. Make the startup script executable:
```bash
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
- Start PostgreSQL and JIRA Docker containers
- Create a sample database schema
- Populate it with Porsche-related mock data
- Create sample JIRA tickets for testing

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

