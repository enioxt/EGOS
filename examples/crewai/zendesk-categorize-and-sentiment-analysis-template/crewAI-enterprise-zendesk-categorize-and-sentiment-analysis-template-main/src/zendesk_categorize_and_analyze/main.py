#!/usr/bin/env python
import sys

from zendesk_categorize_and_analyze.crew import SupportTicketCrew


def run():
    """
    Run the crew to fetch a Zendesk ticket, categorize it, and perform sentiment analysis.
    """
    inputs = {
        "ticket_id": 25,
    }

    # Kicking off the crew
    result = SupportTicketCrew().crew().kickoff(inputs=inputs)

    # Save the result as a Markdown file
    with open("ticket_analysis_report.md", "w") as f:
        f.write(result.raw)


def train():
    """
    Train the crew for a given number of iterations.
    """
    try:
        SupportTicketCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2])
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        SupportTicketCrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and return the results.
    """
    try:
        SupportTicketCrew().crew().test(
            n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2]
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
