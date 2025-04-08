from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool


@CrewBase
class JobChangeMonitorCrew:
    """JobChangeMonitor crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def profile_monitor(self) -> Agent:
        return Agent(
            config=self.agents_config["profile_monitor"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def change_validator(self) -> Agent:
        return Agent(
            config=self.agents_config["change_validator"],
            tools=[SerperDevTool()],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def opportunity_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config["opportunity_analyzer"],
            tools=[],
            allow_delegation=False,
            verbose=True,
        )

    @task
    def monitor_profiles_task(self) -> Task:
        return Task(
            config=self.tasks_config["monitor_profiles_task"],
            agent=self.profile_monitor(),
        )

    @task
    def validate_changes_task(self) -> Task:
        return Task(
            config=self.tasks_config["validate_changes_task"],
            agent=self.change_validator(),
        )

    @task
    def analyze_opportunities_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_opportunities_task"],
            agent=self.opportunity_analyzer(),
            output_file="monitoring_result.json",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the JobChangeMonitor crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
