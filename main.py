import logging
import argparse
from dotenv import load_dotenv

from src.agent.agent import DataAnalysisAgent
from src.models.schemas import JiraTicket, TicketStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_analyzer.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the application."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Data Analysis Automation')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--ticket', type=str, help='Process a specific JIRA ticket ID')
    parser.add_argument('--max-tickets', type=int, default=5, help='Maximum number of tickets to process')
    args = parser.parse_args()
    
    try:
        # Initialize the agent
        agent = DataAnalysisAgent(config_path=args.config)
        
        if args.ticket:
            # Process a specific ticket
            logger.info(f"Processing single ticket: {args.ticket}")
            
            # Create a dummy ticket object
            ticket = JiraTicket(
                ticket_id=args.ticket,
                summary="Manual processing",
                description="Manually triggered data analysis request",
                status=TicketStatus.OPEN
            )
            
            insight = agent.process_ticket(ticket)
            logger.info(f"Processing complete. Insights: {insight.summary}")
            
        else:
            # Process open tickets
            logger.info(f"Processing up to {args.max_tickets} open tickets")
            insights = agent.process_open_tickets(max_tickets=args.max_tickets)
            logger.info(f"Processing complete. Processed {len(insights)} tickets")
            
    except Exception as e:
        logger.error(f"Error in main application: {str(e)}", exc_info=True)
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())
