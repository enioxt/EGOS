#!/usr/bin/env python
import sys

from fraud_detector.crew import FraudDetectorCrew


def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        "customer_name": "John Doe",
        "customer_info": "Company Enterprise",
        "topic": "AI Agents",
    }
    FraudDetectorCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "customer_name": "John Doe",
        "customer_info": "Company Enterprise",
        "topic": "AI Agents",
    }
    try:
        FraudDetectorCrew().crew().train(
            n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        FraudDetectorCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "customer_name": "John Doe",
        "customer_info": "Company Enterprise",
        "topic": "AI Agents",
    }
    try:
        FraudDetectorCrew().crew().test(
            n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
