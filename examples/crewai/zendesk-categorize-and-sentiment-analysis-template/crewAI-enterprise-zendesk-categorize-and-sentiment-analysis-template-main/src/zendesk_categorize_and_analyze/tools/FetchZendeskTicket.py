import os
from typing import Optional, Type

from crewai_tools import BaseTool
from dotenv import load_dotenv
from pydantic.v1 import BaseModel, Field
import requests


class ZendeskTicket(BaseModel):
    id: int
    subject: str
    description: Optional[str] = None  # First comment or ticket body
    status: str
    priority: Optional[str] = None  # Ticket priority (low, normal, high, urgent)
    type: Optional[str] = None  # Ticket type (question, incident, problem, task)
    assignee_id: Optional[int] = None  # ID of the user assigned to the ticket
    requester_id: Optional[int] = None  # ID of the user who requested the ticket
    group_id: Optional[int] = None  # ID of the group assigned to the ticket
    tags: Optional[list[str]] = None  # List of tags associated with the ticket
    organization_id: Optional[int] = None  # ID of the organization
    created_at: str
    updated_at: str
    due_at: Optional[str] = None  # Due date (for tasks)
    external_id: Optional[str] = None  # Optional external ID for linking with other systems
    satisfaction_rating: Optional[dict] = None  # Satisfaction rating info
    via: Optional[dict] = None  # Information on how the ticket was created
    fields: Optional[dict] = None  # Custom fields for your Zendesk account


class ZendeskTicketSearchToolInput(BaseModel):
    """Input schema for ZendeskTicketSearchTool."""

    ticket_id: int = Field(..., description="The specific Zendesk Ticket ID to fetch")


class ZendeskTicketSearchTool(BaseTool):
    name: str = "Fetch Zendesk Ticket by ID"
    description: str = "Fetches a specific Zendesk ticket by its ID using the API."
    args_schema: Type[BaseModel] = ZendeskTicketSearchToolInput

    def _run(self, ticket_id: int) -> Optional[ZendeskTicket]:
        # Load environment variables
        load_dotenv()
        ZENDESK_SUBDOMAIN = os.getenv("ZENDESK_SUBDOMAIN")
        ZENDESK_EMAIL = os.getenv("ZENDESK_EMAIL")
        ZENDESK_API_TOKEN = os.getenv("ZENDESK_API_TOKEN")

        if not ZENDESK_SUBDOMAIN or not ZENDESK_EMAIL or not ZENDESK_API_TOKEN:
            raise ValueError("Zendesk API credentials are not properly set.")

        # Set up the URL and authentication for fetching a specific ticket
        ticket_url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/tickets/{ticket_id}.json"
        auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)

        # Make the GET request to fetch the ticket
        response = requests.get(ticket_url, auth=auth)

        if response.status_code == 200:
            # Parse the ticket data and return the ZendeskTicket object
            ticket_data = response.json().get("ticket", None)
            if ticket_data:
                return ZendeskTicket(**ticket_data)
        elif response.status_code == 404:
            # Ticket not found
            return None
        else:
            # Handle other errors
            print(f"Error: {response.status_code} - {response.text}")
            return None
