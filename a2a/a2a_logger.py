"""
A2A Communication Logger
Tracks agent-to-agent interactions with detailed logging
"""
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class A2AEventType(Enum):
    """Types of A2A events"""
    TASK_ALLOCATION = "task_allocation"  # Agent delegates task to another
    NEGOTIATION = "negotiation"          # Agents negotiate about capability
    MULTI_STEP = "multi_step"            # Sequential multi-agent workflow
    REQUEST = "request"                  # Basic A2A request
    RESPONSE = "response"                # Response to A2A request
    TRANSFER = "transfer"                # Control transfer between agents
    COMPLETION = "completion"            # Task completion notification


@dataclass
class A2AEvent:
    """Represents a single A2A communication event"""
    timestamp: str
    event_type: A2AEventType
    from_agent: str
    to_agent: Optional[str]
    message: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for logging"""
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message": self.message,
            "metadata": self.metadata
        }


class A2ALogger:
    """
    Logs and tracks agent-to-agent communication.
    Provides insights into coordination patterns.
    """
    
    def __init__(self):
        self.events: List[A2AEvent] = []
        self.session_start = datetime.now().isoformat()
    
    def log_event(
        self, 
        event_type: A2AEventType,
        from_agent: str,
        message: str,
        to_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an A2A communication event"""
        event = A2AEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            from_agent=from_agent,
            to_agent=to_agent,
            message=message,
            metadata=metadata or {}
        )
        self.events.append(event)
        
        # Print to console with formatting
        self._print_event(event)
    
    def _print_event(self, event: A2AEvent) -> None:
        """Print event to console with nice formatting"""
        emoji_map = {
            A2AEventType.TASK_ALLOCATION: "[TASK]",
            A2AEventType.NEGOTIATION: "[NEGOTIATE]",
            A2AEventType.MULTI_STEP: "[STEP]",
            A2AEventType.REQUEST: "[REQ]",
            A2AEventType.RESPONSE: "[RESP]",
            A2AEventType.TRANSFER: "[TRANSFER]",
            A2AEventType.COMPLETION: "[DONE]"
        }
        
        emoji = emoji_map.get(event.event_type, "---")
        
        if event.to_agent:
            print(f"    {emoji} [{event.from_agent}] → [{event.to_agent}]: {event.message}")
        else:
            print(f"    {emoji} [{event.from_agent}]: {event.message}")
        
        # Print metadata if present
        if event.metadata:
            for key, value in event.metadata.items():
                print(f"        • {key}: {value}")
    
    def log_task_allocation(
        self,
        from_agent: str,
        to_agents: List[str],
        tasks: Dict[str, str]
    ) -> None:
        """Log task allocation scenario"""
        self.log_event(
            A2AEventType.TASK_ALLOCATION,
            from_agent,
            f"Allocating tasks to {len(to_agents)} agents",
            metadata={"agents": to_agents, "tasks": tasks}
        )
    
    def log_negotiation(
        self,
        from_agent: str,
        to_agent: str,
        request: str,
        outcome: str
    ) -> None:
        """Log negotiation scenario"""
        self.log_event(
            A2AEventType.NEGOTIATION,
            from_agent,
            f"Negotiating: {request}",
            to_agent=to_agent,
            metadata={"outcome": outcome}
        )
    
    def log_multi_step(
        self,
        coordinator: str,
        steps: List[Dict[str, str]]
    ) -> None:
        """Log multi-step workflow"""
        self.log_event(
            A2AEventType.MULTI_STEP,
            coordinator,
            f"Executing {len(steps)}-step workflow",
            metadata={"steps": steps}
        )
    
    def log_request(
        self,
        from_agent: str,
        to_agent: str,
        query: str
    ) -> None:
        """Log basic A2A request"""
        self.log_event(
            A2AEventType.REQUEST,
            from_agent,
            query,
            to_agent=to_agent
        )
    
    def log_response(
        self,
        from_agent: str,
        to_agent: str,
        summary: str
    ) -> None:
        """Log A2A response"""
        self.log_event(
            A2AEventType.RESPONSE,
            from_agent,
            summary,
            to_agent=to_agent
        )
    
    def log_transfer(
        self,
        from_agent: str,
        to_agent: str,
        reason: str
    ) -> None:
        """Log control transfer"""
        self.log_event(
            A2AEventType.TRANSFER,
            from_agent,
            reason,
            to_agent=to_agent
        )
    
    def log_completion(
        self,
        agent: str,
        summary: str
    ) -> None:
        """Log task completion"""
        self.log_event(
            A2AEventType.COMPLETION,
            agent,
            summary
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of A2A communication"""
        event_counts = {}
        for event in self.events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            "session_start": self.session_start,
            "total_events": len(self.events),
            "event_counts": event_counts,
            "agents_involved": list(set(
                [e.from_agent for e in self.events] + 
                [e.to_agent for e in self.events if e.to_agent]
            ))
        }
    
    def print_summary(self) -> None:
        """Print communication summary"""
        summary = self.get_summary()
        
        print("\n" + "=" * 70)
        print("  A2A COMMUNICATION SUMMARY")
        print("=" * 70)
        print(f"\nSession Start: {summary['session_start']}")
        print(f"Total Events: {summary['total_events']}")
        print("\nEvent Breakdown:")
        for event_type, count in summary['event_counts'].items():
            print(f"  • {event_type}: {count}")
        print("\nAgents Involved:")
        for agent in summary['agents_involved']:
            print(f"  • {agent}")
        print("=" * 70 + "\n")
    
    def export_log(self, filepath: str) -> None:
        """Export log to JSON file"""
        log_data = {
            "session_start": self.session_start,
            "events": [event.to_dict() for event in self.events],
            "summary": self.get_summary()
        }
        
        with open(filepath, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"A2A log exported to {filepath}")
    
    def clear(self) -> None:
        """Clear all logged events"""
        self.events = []
        self.session_start = datetime.now().isoformat()


# Global logger instance
_global_logger: Optional[A2ALogger] = None


def get_a2a_logger() -> A2ALogger:
    """Get or create global A2A logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = A2ALogger()
    return _global_logger


def reset_a2a_logger() -> None:
    """Reset the global logger"""
    global _global_logger
    _global_logger = A2ALogger()


# Convenience functions
def log_task_allocation(from_agent: str, to_agents: List[str], tasks: Dict[str, str]) -> None:
    """Convenience: Log task allocation"""
    get_a2a_logger().log_task_allocation(from_agent, to_agents, tasks)


def log_negotiation(from_agent: str, to_agent: str, request: str, outcome: str) -> None:
    """Convenience: Log negotiation"""
    get_a2a_logger().log_negotiation(from_agent, to_agent, request, outcome)


def log_multi_step(coordinator: str, steps: List[Dict[str, str]]) -> None:
    """Convenience: Log multi-step workflow"""
    get_a2a_logger().log_multi_step(coordinator, steps)


def log_request(from_agent: str, to_agent: str, query: str) -> None:
    """Convenience: Log A2A request"""
    get_a2a_logger().log_request(from_agent, to_agent, query)


def log_response(from_agent: str, to_agent: str, summary: str) -> None:
    """Convenience: Log A2A response"""
    get_a2a_logger().log_response(from_agent, to_agent, summary)


def log_transfer(from_agent: str, to_agent: str, reason: str) -> None:
    """Convenience: Log control transfer"""
    get_a2a_logger().log_transfer(from_agent, to_agent, reason)


def log_completion(agent: str, summary: str) -> None:
    """Convenience: Log task completion"""
    get_a2a_logger().log_completion(agent, summary)


def print_a2a_summary() -> None:
    """Convenience: Print communication summary"""
    get_a2a_logger().print_summary()


def export_a2a_log(filepath: str) -> None:
    """Convenience: Export log to file"""
    get_a2a_logger().export_log(filepath)

