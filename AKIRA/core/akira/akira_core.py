"""
AKIRA Core - Main Orchestrator
Autonomous AI Partner System
"""

import asyncio
from typing import Dict, Any, Optional
from core.akira.model_manager import ModelManager
from core.akira.interview_agent import InterviewAgent
from core.akira.terminal_executor import TerminalExecutor
from core.akira.financial_manager import FinancialManager
from core.akira.idea_generator import IdeaGenerator


class AKIRACore:
    """
    AKIRA-9: Autonomous AI Partner

    Main orchestrator that coordinates all modules.
    """

    def __init__(self):
        # Initialize all modules
        self.model_manager = ModelManager()
        self.interview_agent = InterviewAgent(min_questions=3, max_questions=7)
        self.terminal_executor = TerminalExecutor(timeout=600)
        self.financial_manager = FinancialManager(
            revenue_share=0.30,
            max_single_purchase=1000.0,
            approval_threshold=5000.0
        )
        self.idea_generator = IdeaGenerator(self.model_manager)

        self.active = True
        self.current_task = None

    async def process_request(self, user_request: str) -> Dict[str, Any]:
        """
        Main entry point for processing user requests.

        Workflow:
        1. Conduct interview (audit request)
        2. Plan execution
        3. Execute through appropriate tools
        4. Report results

        Args:
            user_request: User's request/task

        Returns:
            Execution result
        """
        # Step 1: Interview to understand request 100%
        interview_result = await self.interview_agent.conduct_interview(
            user_request,
            self.model_manager
        )

        if not interview_result.ready_to_execute:
            return {
                "success": False,
                "message": "Need more information",
                "confidence": interview_result.confidence,
                "questions": interview_result.questions_asked
            }

        # Step 2: Determine execution strategy
        strategy = await self._plan_execution(interview_result.clarified_request)

        # Step 3: Execute
        result = await self._execute_strategy(strategy)

        return result

    async def _plan_execution(self, request: str) -> Dict[str, Any]:
        """Plan how to execute the request."""
        prompt = f"""
        Request: {request}

        Determine:
        1. Best tool (claude, codex, or both)
        2. Execution steps
        3. Estimated cost

        Return as JSON.
        """

        response = await self.model_manager.query_model("gpt-4", prompt)

        # Simplified - in production would parse JSON properly
        return {
            "tool": "claude",
            "steps": ["analyze", "implement", "test"],
            "estimated_cost": 0.0
        }

    async def _execute_strategy(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the planned strategy."""
        tool = strategy.get("tool", "claude")

        if tool == "claude":
            result = await self.terminal_executor.execute_claude(
                task_description=str(strategy)
            )
            return {
                "success": result.success,
                "output": result.output,
                "error": result.error
            }

        return {"success": False, "error": "Unknown tool"}

    async def generate_business_ideas(self, context: str = "") -> list:
        """Generate business ideas autonomously."""
        ideas = await self.idea_generator.generate_ideas(context=context, count=5)
        return ideas

    def get_status(self) -> Dict[str, Any]:
        """Get AKIRA system status."""
        return {
            "active": self.active,
            "financial_status": self.financial_manager.get_financial_status(),
            "models_available": self.model_manager.models_available,
            "current_task": self.current_task
        }
