from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from pydantic import BaseModel, Field


class RiskAssesment(BaseModel):
    """Risk Assesment model for the Fraud Detector crew."""

    risk_score: float = Field(..., description="The risk score of the lead between 0 - 10")
    risk_summary: str = Field(..., description="The summary of the risk of the lead")
    risk_factors: List[str] = Field(
        ..., description="The factors that contribute to the risk score"
    )


@CrewBase
class FraudDetectorCrew:
    """Fraud Detection crew configured to identify and assess potential fraud activities."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def financial_forensics_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["financial_forensics_analyst"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            verbose=True,
        )

    @agent
    def compliance_officer(self) -> Agent:
        return Agent(
            config=self.agents_config["compliance_officer"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            verbose=True,
        )

    @agent
    def risk_assessment_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["risk_assessment_analyst"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            verbose=True,
        )

    @task
    def financial_forensics_task(self) -> Task:
        return Task(
            config=self.tasks_config["financial_forensics_analyst_task"],
            agent=self.financial_forensics_analyst(),
        )

    @task
    def compliance_task(self) -> Task:
        return Task(
            config=self.tasks_config["compliance_officer_task"],
            agent=self.compliance_officer(),
        )

    @task
    def risk_assessment_task(self) -> Task:
        return Task(
            config=self.tasks_config["risk_assessment_analyst_task"],
            agent=self.risk_assessment_analyst(),
            output_json=RiskAssesment,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Fraud Detection crew"""
        return Crew(
            agents=[
                self.financial_forensics_analyst(),
                self.compliance_officer(),
                self.risk_assessment_analyst(),
            ],
            tasks=[
                self.financial_forensics_task(),
                self.compliance_task(),
                self.risk_assessment_task(),
            ],
            process=Process.sequential,
            verbose=True,
        )
