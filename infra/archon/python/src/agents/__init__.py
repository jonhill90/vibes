"""
Agents module for PydanticAI-powered agents in the Archon system.

This module contains various specialized agents for different tasks:
- DocumentAgent: Processes and validates project documentation
- PlanningAgent: Generates feature plans and technical specifications
- ERDAgent: Creates entity relationship diagrams
- TaskAgent: Generates and manages project tasks

All agents are built using PydanticAI for type safety and structured outputs.
"""

from .base_agent import BaseAgent
from .document_agent import DocumentAgent

__all__ = ["BaseAgent", "DocumentAgent"]
