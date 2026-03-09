"""
Agent Logging System

This module provides a logging class for tracking agent actions, decisions,
and reasoning throughout a session. Logs are saved as JSON for later review.
"""

import os
import json
from datetime import datetime


class AgentLogger:
    """
    Tracks all agent actions, decisions, and reasoning.
    Saves to JSON file for later review.

    Why Logging?
    - Debugging: Understanding why the agent made certain decisions
    - Learning: Reviewing how AI agents reason about problems
    - Transparency: Auditing agent actions for compliance or research
    - Improvement: Identifying patterns to improve agent behavior

    Example:
        logger = AgentLogger()
        logger.log_thought("User asked about coffee shops")
        logger.log_action("query_places", approved=True, result="Found 50 places")
        logger.log_summary("Found 50 coffee shops in Seattle")
        logger.save_to_file()
    """

    def __init__(self):
        """Initialize a new logging session."""
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logs = []
        self.start_time = datetime.now().isoformat()

        print(f"Logger initialized - Session ID: {self.session_id}")

    def log_thought(self, thought: str) -> None:
        """
        Log an agent's reasoning or thought process.

        Args:
            thought: The agent's reasoning or thought
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'thought',
            'content': thought
        }
        self.logs.append(entry)
        print(f"\nAgent thinking: {thought}")

    def log_action(self, action: str, approved: bool, result: str) -> None:
        """
        Log an action the agent took or attempted.

        Args:
            action: Description of the action
            approved: Whether the action was approved by human
            result: The result or outcome of the action
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'action',
            'action': action,
            'approved': approved,
            'result': result
        }
        self.logs.append(entry)

        status = "APPROVED" if approved else "REJECTED"
        print(f"\n[{status}] Action logged: {action}")

    def log_summary(self, summary: str) -> None:
        """
        Log a summary or conclusion.

        Args:
            summary: The summary text
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'summary',
            'content': summary
        }
        self.logs.append(entry)
        print(f"\nSummary logged")

    def save_to_file(self, logs_dir: str = 'logs') -> str:
        """
        Save all logs to a JSON file.

        Args:
            logs_dir: Directory to save logs in (default: 'logs')

        Returns:
            Path to the saved log file

        Example:
            log_file = logger.save_to_file()
            print(f"Logs saved to: {log_file}")
        """
        # Ensure logs directory exists
        os.makedirs(logs_dir, exist_ok=True)

        # Create log data structure
        log_data = {
            'session_id': self.session_id,
            'start_time': self.start_time,
            'end_time': datetime.now().isoformat(),
            'total_entries': len(self.logs),
            'logs': self.logs
        }

        # Save to file
        filename = f"{logs_dir}/agent_session_{self.session_id}.json"
        with open(filename, 'w') as f:
            json.dump(log_data, f, indent=2)

        print(f"\nLogs saved to: {filename}")
        print(f"Total log entries: {len(self.logs)}")

        return filename

    def get_logs(self) -> list:
        """
        Get all logs for this session.

        Returns:
            List of log entries
        """
        return self.logs.copy()

    def clear_logs(self) -> None:
        """Clear all logs for this session."""
        self.logs = []
        print("Logs cleared")
