from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from zendesk_categorize_and_analyze.tools.FetchZendeskTicket import (
    ZendeskTicketSearchTool,
)


@CrewBase
class SupportTicketCrew:
    """CrewAI Support Ticket Analysis Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def zendesk_ticket_fetcher_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["zendesk_ticket_fetcher_agent"],
            tools=[ZendeskTicketSearchTool()],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def zendesk_ticket_analyzer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["zendesk_ticket_analyzer_agent"],
            tools=[],
            allow_delegation=False,
            verbose=True,
        )

    @task
    def fetch_zendesk_ticket_task(self) -> Task:
        return Task(
            config=self.tasks_config["fetch_zendesk_ticket_task"],
            agent=self.zendesk_ticket_fetcher_agent(),
        )

    @task
    def categorize_and_analyze_ticket_task(self) -> Task:
        return Task(
            config=self.tasks_config["categorize_and_analyze_ticket_task"],
            agent=self.zendesk_ticket_analyzer_agent(),
            output_file="ticket_analysis_report.md",  # File to save the summary
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Support Ticket Analysis Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # Tasks will run sequentially
            verbose=True,
        )
