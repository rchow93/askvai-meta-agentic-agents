#!/usr/bin/env python3
"""
Electric Vehicle News Summarizer Crew

This script creates a crew of AI agents to collect, summarize, analyze, and format
information about recent developments in the electric vehicle industry.
"""

import os
import sys
import logging
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from crewai import Agent, Task, Crew, LLM
    from crewai_tools import (
        SerperDevTool,
        WebsiteSearchTool,
        FileReadTool,
    )
except ImportError:
    logger.error("Required libraries not found. Please install them using:")
    logger.error("pip install crewai crewai-tools")
    sys.exit(1)

# API key setup
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY environment variable not set")
    logger.error("Please set it with: export OPENAI_API_KEY=your_key_here")
    sys.exit(1)

# LLM Setup
try:
    llm = LLM(model="gpt-4o-mini", api_key=OPENAI_API_KEY)
except Exception as e:
    logger.error(f"Error initializing LLM: {e}")
    sys.exit(1)

# Initialize tools
tools = {}
try:
    if SERPER_API_KEY:
        tools["serper"] = SerperDevTool()
    tools["website"] = WebsiteSearchTool()
    tools["fileread"] = FileReadTool()
except Exception as e:
    logger.error(f"Error initializing tools: {e}")
    logger.warning("Continuing with limited functionality")

# Define Agents
news_researcher = Agent(
    role="EV News Researcher",
    goal="Collect recent news articles about electric vehicles from a variety of reputable sources.",
    backstory="""With a background in communications and a passion for sustainable technology, 
    you thrive on sifting through vast amounts of information to find the most relevant and 
    impactful news. You have a keen eye for detail and enjoy uncovering stories that not only 
    inform but inspire change in the electric vehicle sector.""",
    verbose=True,
    llm=llm,
    tools=[tools.get("serper", None), tools.get("website", None)]
)

content_summarizer = Agent(
    role="Content Summarizer",
    goal="Summarize the collected news articles, highlighting key points and trends in the electric vehicle industry.",
    backstory="""An experienced content writer with a knack for distilling complex information 
    into digestible formats, you have worked in journalism and digital content creation. 
    You are driven by the need to make crucial industry information accessible to all, ensuring 
    that each summary engages the reader while providing essential insights.""",
    verbose=True,
    llm=llm
)

trend_analyst = Agent(
    role="EV Industry Analyst",
    goal="Analyze the article summaries to synthesize overarching trends and insights in the electric vehicle sector.",
    backstory="""With a robust analytical background and expertise in market research, 
    you are passionate about innovation in the automotive field. You excel at connecting 
    the dots between various sources and extracting meaningful patterns that shape the 
    future of electric mobility. Your strategic foresight allows organizations to stay 
    ahead of the curve in this rapidly evolving market.""",
    verbose=True,
    llm=llm
)

# Define Tasks
research_task = Task(
    description="""Find the most relevant and recent news articles about electric vehicles.
        Focus on major developments from the past month, including:
        - New vehicle announcements
        - Battery technology advancements
        - Industry partnerships and acquisitions
        - Regulatory changes affecting EVs
        - Market trends and sales data

        For each article, note the source, date, and key points.""",
    agent=news_researcher,
    expected_output="A compiled list of at least 10-15 recent articles with their titles, publication dates, sources, and brief descriptions."
)

summarize_task = Task(
    description="""Create concise summaries of each news article provided by the researcher.
        Each summary should:
        - Capture the essential information in 2-3 paragraphs
        - Highlight what makes this news significant
        - Use clear, accessible language
        - Include relevant context where necessary""",
    agent=content_summarizer,
    expected_output="A set of article summaries (approximately 200-300 words each) that captures the essence of each news article."
)

analyze_task = Task(
    description="""Analyze the collected news to identify important trends and implications.
        Your analysis should:
        - Identify 3-5 key trends emerging from the recent news
        - Explain how these developments might impact different stakeholders (consumers, manufacturers, investors, etc.)
        - Discuss any contradictions or tensions in industry directions
        - Provide context about how these developments fit into long-term EV market evolution""",
    agent=trend_analyst,
    expected_output="A comprehensive analysis of trends in the electric vehicle sector with insights about their implications."
)

# Create Crew
ev_news_crew = Crew(
    agents=[news_researcher, content_summarizer, trend_analyst],
    tasks=[research_task, summarize_task, analyze_task],
    verbose=True
)


def main():
    """Main function to run the Electric Vehicle News Summarizer Crew."""
    print("Starting the Electric Vehicle News Summarizer Crew...")

    try:
        # Execute the crew
        result = ev_news_crew.kickoff()

        # Save the result to a file
        with open("ev_news_summary.md", "w") as f:
            f.write(str(result))

        print("\nExecution completed successfully!")
        print("The EV news summary has been saved to 'ev_news_summary.md'")

    except Exception as e:
        logger.error(f"An error occurred during execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()