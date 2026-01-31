"""
AKIRA Interview Agent
Conducts audit of user requests to ensure 100% understanding
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class InterviewResult:
    """Result of interview process."""
    original_request: str
    clarified_request: str
    questions_asked: List[str]
    answers: List[str]
    confidence: float  # 0.0 to 1.0
    ready_to_execute: bool


class InterviewAgent:
    """
    Conducts short audit with user to understand request 100%.
    Asks 3-7 clarifying questions before execution.
    """

    def __init__(self, min_questions: int = 3, max_questions: int = 7):
        self.min_questions = min_questions
        self.max_questions = max_questions

    async def conduct_interview(
        self,
        user_request: str,
        model_manager
    ) -> InterviewResult:
        """
        Conduct interview to clarify user request.

        Args:
            user_request: Original user request
            model_manager: ModelManager instance for generating questions

        Returns:
            InterviewResult with clarified understanding
        """
        questions = await self._generate_questions(user_request, model_manager)
        answers = []

        # In real implementation, this would interact with user
        # For now, placeholder for the interaction loop

        clarified_request = await self._build_clarified_request(
            user_request,
            questions,
            answers,
            model_manager
        )

        confidence = self._calculate_confidence(questions, answers)

        return InterviewResult(
            original_request=user_request,
            clarified_request=clarified_request,
            questions_asked=questions,
            answers=answers,
            confidence=confidence,
            ready_to_execute=confidence >= 0.9
        )

    async def _generate_questions(
        self,
        request: str,
        model_manager
    ) -> List[str]:
        """Generate clarifying questions about the request."""
        prompt = f"""
        User request: {request}

        Generate {self.min_questions}-{self.max_questions} clarifying questions to understand:
        - Exact requirements
        - Success criteria
        - Constraints
        - Timeline
        - Budget

        Return only questions, one per line.
        """

        response = await model_manager.query_model("gpt-4", prompt)

        if response["success"]:
            questions = [q.strip() for q in response["response"].split("\n") if q.strip()]
            return questions[:self.max_questions]

        return self._get_default_questions()

    def _get_default_questions(self) -> List[str]:
        """Default questions if generation fails."""
        return [
            "What is the main goal of this project?",
            "What are the success criteria?",
            "Are there any specific constraints or requirements?",
            "What is the expected timeline?",
            "What is the budget range?"
        ]

    async def _build_clarified_request(
        self,
        original: str,
        questions: List[str],
        answers: List[str],
        model_manager
    ) -> str:
        """Build clarified request from Q&A."""
        qa_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(questions, answers)])

        prompt = f"""
        Original request: {original}

        Clarifications:
        {qa_text}

        Synthesize into a clear, detailed project specification.
        """

        response = await model_manager.query_model("gpt-4", prompt)

        if response["success"]:
            return response["response"]

        return original

    def _calculate_confidence(self, questions: List[str], answers: List[str]) -> float:
        """Calculate confidence in understanding (0.0 to 1.0)."""
        if not answers:
            return 0.0

        # Simple heuristic: more detailed answers = higher confidence
        avg_answer_length = sum(len(a) for a in answers) / len(answers)

        if avg_answer_length > 100:
            return 0.95
        elif avg_answer_length > 50:
            return 0.85
        elif avg_answer_length > 20:
            return 0.75
        else:
            return 0.60
