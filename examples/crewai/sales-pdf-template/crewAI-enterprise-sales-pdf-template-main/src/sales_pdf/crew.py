from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool


@CrewBase
class SalesPdfCrew:
    """CrewAI Sales PDF Creation Crew"""

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
    def company_product_researcher_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["company_product_researcher_agent"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def content_creator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["content_creator_agent"],
            tools=[],
            allow_delegation=False,
            verbose=True,
        )

    @task
    def research_lead_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_lead_task"],
            agent=self.lead_researcher_agent(),
        )

    @task
    def research_company_product_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_company_product_task"],
            agent=self.company_product_researcher_agent(),
        )

    @task
    def create_pdf_content_task(self) -> Task:
        return Task(
            config=self.tasks_config["create_pdf_content_task"],
            agent=self.content_creator_agent(),
            output_file="sales_pdf_text.md",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Sales PDF Creation Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
