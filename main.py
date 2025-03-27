# main.py
# !/usr/bin/env python
import os
import sys

# Import the necessary classes from crew.py
from crew import CrewCreationFlow, CrewCreationState
from llms import available_llms, get_llm


def run():
    """
    Run the crew creation process.
    """
    print("Welcome to the CrewAI Meta-Crew Generator!")

    user_problem = input(
        "Describe the problem you want your CrewAI crew to solve, or the code/tool you want to generate: ")

    # Select LLMs for worker and supervisor agents
    print("\nAvailable LLMs:")
    for i, llm_name in enumerate(available_llms.keys()):
        print(f"{i + 1}. {llm_name}")

    worker_llm_name = None
    supervisor_llm_name = None

    while True:
        try:
            worker_choice = input("Select an LLM for the WORKER agents (enter number): ")
            worker_index = int(worker_choice) - 1
            if 0 <= worker_index < len(available_llms):
                worker_llm_name = list(available_llms.keys())[worker_index]
                break
            else:
                print("Invalid choice. Please enter a number from the list.")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a number from the list.")

    while True:
        try:
            supervisor_choice = input("Select an LLM for the SUPERVISOR agent (enter number): ")
            supervisor_index = int(supervisor_choice) - 1
            if 0 <= supervisor_index < len(available_llms):
                supervisor_llm_name = list(available_llms.keys())[supervisor_index]
                break
            else:
                print("Invalid choice. Please enter a number from the list.")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a number from the list.")

    # Create initial state with user input and selected LLMs
    initial_state = CrewCreationState(
        user_input=user_problem,
        worker_llm=worker_llm_name,
        supervisor_llm=supervisor_llm_name
    )

    # Create and start the flow
    flow = CrewCreationFlow(initial_state)
    flow.kickoff()


if __name__ == "__main__":
    run()