from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from zendesk_ticket_analysis.tools.FetchZendeskTickets import ZendeskTicketSearchTool


@CrewBase
class ZendeskTicketAnalysisCrew:
    """CrewAI Ticket Analysis Crew"""

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
    def pull_zendesk_tickets_task(self) -> Task:
        return Task(
            config=self.tasks_config["pull_zendesk_tickets_task"],
            agent=self.zendesk_ticket_fetcher_agent(),
        )

    @task
    def summarize_tickets_task(self) -> Task:
        return Task(
            config=self.tasks_config["summarize_tickets_task"],
            agent=self.zendesk_ticket_analyzer_agent(),
            output_file="ticket_summary.md",  # File to save the summary
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Ticket Analysis Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # Tasks will run sequentially
            verbose=True,
        )
