import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import uuid

class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TicketCategory(Enum):
    INSTALLATION = "installation"
    PERFORMANCE = "performance"
    FEATURE = "feature"
    BUG = "bug"
    QUESTION = "question"
    OTHER = "other"

class SupportTicket:
    def __init__(self, 
                 title: str,
                 description: str,
                 category: TicketCategory,
                 priority: TicketPriority = TicketPriority.MEDIUM,
                 user_email: Optional[str] = None):
        """Initialize a support ticket."""
        self.ticket_id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.category = category
        self.priority = priority
        self.status = TicketStatus.OPEN
        self.user_email = user_email
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.assigned_to = None
        self.comments = []
        self.resolution = None

    def to_dict(self) -> Dict:
        """Convert ticket to dictionary."""
        return {
            "ticket_id": self.ticket_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "user_email": self.user_email,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "assigned_to": self.assigned_to,
            "comments": self.comments,
            "resolution": self.resolution
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'SupportTicket':
        """Create ticket from dictionary."""
        ticket = cls(
            title=data["title"],
            description=data["description"],
            category=TicketCategory(data["category"]),
            priority=TicketPriority(data["priority"]),
            user_email=data["user_email"]
        )
        ticket.ticket_id = data["ticket_id"]
        ticket.status = TicketStatus(data["status"])
        ticket.created_at = data["created_at"]
        ticket.updated_at = data["updated_at"]
        ticket.assigned_to = data["assigned_to"]
        ticket.comments = data["comments"]
        ticket.resolution = data["resolution"]
        return ticket

class TicketSystem:
    def __init__(self, storage_dir: str = "docs/support/tickets"):
        """Initialize the ticket system."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def create_ticket(self, 
                     title: str,
                     description: str,
                     category: TicketCategory,
                     priority: TicketPriority = TicketPriority.MEDIUM,
                     user_email: Optional[str] = None) -> SupportTicket:
        """Create a new support ticket."""
        ticket = SupportTicket(title, description, category, priority, user_email)
        self._save_ticket(ticket)
        return ticket

    def update_ticket(self, ticket: SupportTicket) -> None:
        """Update an existing ticket."""
        ticket.updated_at = datetime.now().isoformat()
        self._save_ticket(ticket)

    def add_comment(self, ticket_id: str, comment: str, author: str) -> None:
        """Add a comment to a ticket."""
        ticket = self.get_ticket(ticket_id)
        if ticket:
            comment_data = {
                "author": author,
                "content": comment,
                "timestamp": datetime.now().isoformat()
            }
            ticket.comments.append(comment_data)
            self.update_ticket(ticket)

    def assign_ticket(self, ticket_id: str, assignee: str) -> None:
        """Assign a ticket to someone."""
        ticket = self.get_ticket(ticket_id)
        if ticket:
            ticket.assigned_to = assignee
            ticket.status = TicketStatus.IN_PROGRESS
            self.update_ticket(ticket)

    def resolve_ticket(self, ticket_id: str, resolution: str) -> None:
        """Mark a ticket as resolved."""
        ticket = self.get_ticket(ticket_id)
        if ticket:
            ticket.status = TicketStatus.RESOLVED
            ticket.resolution = resolution
            self.update_ticket(ticket)

    def close_ticket(self, ticket_id: str) -> None:
        """Close a ticket."""
        ticket = self.get_ticket(ticket_id)
        if ticket:
            ticket.status = TicketStatus.CLOSED
            self.update_ticket(ticket)

    def get_ticket(self, ticket_id: str) -> Optional[SupportTicket]:
        """Get a ticket by ID."""
        ticket_file = self.storage_dir / f"{ticket_id}.json"
        if ticket_file.exists():
            try:
                with open(ticket_file, 'r') as f:
                    data = json.load(f)
                return SupportTicket.from_dict(data)
            except Exception as e:
                self.logger.error(f"Error reading ticket {ticket_id}: {str(e)}")
        return None

    def get_tickets(self, 
                   status: Optional[TicketStatus] = None,
                   category: Optional[TicketCategory] = None,
                   priority: Optional[TicketPriority] = None) -> List[SupportTicket]:
        """Get tickets with optional filters."""
        tickets = []
        for ticket_file in self.storage_dir.glob("*.json"):
            try:
                with open(ticket_file, 'r') as f:
                    data = json.load(f)
                ticket = SupportTicket.from_dict(data)
                
                # Apply filters
                if status and ticket.status != status:
                    continue
                if category and ticket.category != category:
                    continue
                if priority and ticket.priority != priority:
                    continue
                
                tickets.append(ticket)
            except Exception as e:
                self.logger.error(f"Error reading ticket file {ticket_file}: {str(e)}")
        
        return tickets

    def _save_ticket(self, ticket: SupportTicket) -> None:
        """Save ticket to file."""
        ticket_file = self.storage_dir / f"{ticket.ticket_id}.json"
        try:
            with open(ticket_file, 'w') as f:
                json.dump(ticket.to_dict(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving ticket {ticket.ticket_id}: {str(e)}")

    def generate_report(self) -> Dict:
        """Generate a report of ticket statistics."""
        tickets = self.get_tickets()
        
        report = {
            "total_tickets": len(tickets),
            "status_counts": {status.value: 0 for status in TicketStatus},
            "category_counts": {category.value: 0 for category in TicketCategory},
            "priority_counts": {priority.value: 0 for priority in TicketPriority},
            "average_resolution_time": 0,
            "open_tickets": 0
        }
        
        resolution_times = []
        
        for ticket in tickets:
            report["status_counts"][ticket.status.value] += 1
            report["category_counts"][ticket.category.value] += 1
            report["priority_counts"][ticket.priority.value] += 1
            
            if ticket.status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]:
                report["open_tickets"] += 1
            
            if ticket.status == TicketStatus.RESOLVED and ticket.resolution:
                created = datetime.fromisoformat(ticket.created_at)
                resolved = datetime.fromisoformat(ticket.updated_at)
                resolution_time = (resolved - created).total_seconds() / 3600  # hours
                resolution_times.append(resolution_time)
        
        if resolution_times:
            report["average_resolution_time"] = sum(resolution_times) / len(resolution_times)
        
        return report
