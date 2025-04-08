from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool


@CrewBase
class PrepForMeetingCrew:
    """CrewAI Meeting Preparation Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def lead_researcher_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["lead_researcher_agent"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def product_specialist_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["product_specialist_agent"],
            tools=[SerperDevTool()],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def sales_strategist_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["sales_strategist_agent"],
            tools=[SerperDevTool()],
            verbose=True,
        )

    @agent
    def briefing_coordinator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["briefing_coordinator_agent"],
            tools=[],
            verbose=True,
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
            agent=self.lead_researcher_agent(),
        )

    @task
    def product_alignment_task(self) -> Task:
        return Task(
            config=self.tasks_config["product_alignment_task"],
            agent=self.product_specialist_agent(),
        )

    @task
    def sales_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config["sales_strategy_task"],
            agent=self.sales_strategist_agent(),
        )

    @task
    def meeting_preparation_task(self) -> Task:
        return Task(
            config=self.tasks_config["meeting_preparation_task"],
            agent=self.briefing_coordinator_agent(),
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Meeting Preparation Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
