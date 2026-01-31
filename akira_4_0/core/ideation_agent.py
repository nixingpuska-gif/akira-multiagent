"""
AKIRA 4.0 Ideation Agent
Specialized agent for achieving 90% project clarity through structured dialogue.
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ClarityPhase(Enum):
    INITIAL = "initial"
    DEEP_DIVE = "deep_dive"
    VALIDATION = "validation"
    COMPLETE = "complete"

@dataclass
class ProjectRequirements:
    core_problem: Optional[str] = None
    target_users: Optional[str] = None
    key_features: Optional[List[str]] = None
    success_metrics: Optional[List[str]] = None
    timeline: Optional[str] = None
    technical_constraints: Optional[str] = None
    integrations: Optional[List[str]] = None
    scalability: Optional[str] = None
    security_requirements: Optional[str] = None
    support_needs: Optional[str] = None
    
    def clarity_score(self) -> float:
        """Calculate clarity score (0-1) based on filled fields."""
        filled_fields = sum(1 for v in asdict(self).values() if v is not None)
        total_fields = len(asdict(self))
        return filled_fields / total_fields

class IdeationAgent:
    """
    Specialized agent for project ideation and requirement gathering.
    Achieves 90% clarity before system execution begins.
    """
    
    def __init__(self):
        self.clarity_threshold = 0.90
        self.max_questions = 20
        self.questions_asked = 0
        self.current_phase = ClarityPhase.INITIAL
        self.requirements = ProjectRequirements()
        
        # Question templates for each phase
        self.initial_questions = [
            "What is the core problem you're solving?",
            "Who is your target user or market?",
            "What are your top 3 key features?",
            "How will you measure success?",
            "What is your timeline for this project?"
        ]
        
        self.deep_dive_questions = [
            "What are your technical constraints (budget, infrastructure)?",
            "What integrations or APIs do you need?",
            "What are your scalability expectations?",
            "What security or compliance requirements do you have?",
            "What post-launch support do you need?"
        ]
    
    def start_ideation(self, initial_idea: str) -> Dict:
        """
        Start the ideation process with user's initial idea.
        Returns the first question.
        """
        self.current_phase = ClarityPhase.INITIAL
        self.questions_asked = 0
        self.requirements = ProjectRequirements()
        
        logger.info(f"Starting ideation for: {initial_idea}")
        
        return {
            "phase": self.current_phase.value,
            "message": "Great! Let's clarify your project idea. I'll ask some questions to achieve 90% clarity.",
            "question": self.initial_questions[0],
            "question_number": 1,
            "total_questions_estimate": len(self.initial_questions) + len(self.deep_dive_questions)
        }
    
    def process_answer(self, answer: str, question_index: int) -> Dict:
        """
        Process user's answer and generate next question.
        """
        self.questions_asked += 1
        
        # Map answer to requirement field
        if self.current_phase == ClarityPhase.INITIAL:
            self._process_initial_answer(answer, question_index)
            
            # Check if we should move to deep dive
            if question_index >= len(self.initial_questions) - 1:
                self.current_phase = ClarityPhase.DEEP_DIVE
                next_question = self.deep_dive_questions[0]
                next_index = 0
            else:
                next_question = self.initial_questions[question_index + 1]
                next_index = question_index + 1
        
        elif self.current_phase == ClarityPhase.DEEP_DIVE:
            self._process_deep_dive_answer(answer, question_index)
            
            # Check if we should move to validation
            if question_index >= len(self.deep_dive_questions) - 1:
                self.current_phase = ClarityPhase.VALIDATION
                return self._generate_validation_response()
            else:
                next_question = self.deep_dive_questions[question_index + 1]
                next_index = question_index + 1
        
        else:
            return {"error": "Invalid phase"}
        
        # Check if we've exceeded max questions
        if self.questions_asked >= self.max_questions:
            logger.warning("Max questions reached. Moving to validation.")
            self.current_phase = ClarityPhase.VALIDATION
            return self._generate_validation_response()
        
        return {
            "phase": self.current_phase.value,
            "message": f"Got it. {answer}",
            "question": next_question,
            "question_number": self.questions_asked + 1,
            "clarity_score": self.requirements.clarity_score(),
            "total_questions_estimate": len(self.initial_questions) + len(self.deep_dive_questions)
        }
    
    def _process_initial_answer(self, answer: str, question_index: int) -> None:
        """Process answers from initial phase."""
        if question_index == 0:
            self.requirements.core_problem = answer
        elif question_index == 1:
            self.requirements.target_users = answer
        elif question_index == 2:
            self.requirements.key_features = self._parse_list(answer)
        elif question_index == 3:
            self.requirements.success_metrics = self._parse_list(answer)
        elif question_index == 4:
            self.requirements.timeline = answer
    
    def _process_deep_dive_answer(self, answer: str, question_index: int) -> None:
        """Process answers from deep dive phase."""
        if question_index == 0:
            self.requirements.technical_constraints = answer
        elif question_index == 1:
            self.requirements.integrations = self._parse_list(answer)
        elif question_index == 2:
            self.requirements.scalability = answer
        elif question_index == 3:
            self.requirements.security_requirements = answer
        elif question_index == 4:
            self.requirements.support_needs = answer
    
    def _parse_list(self, text: str) -> List[str]:
        """Parse comma-separated or newline-separated list."""
        items = [item.strip() for item in text.replace('\n', ',').split(',')]
        return [item for item in items if item]
    
    def _generate_validation_response(self) -> Dict:
        """Generate validation summary and ask for confirmation."""
        summary = self._generate_summary()
        clarity = self.requirements.clarity_score()
        
        if clarity >= self.clarity_threshold:
            status = "ready"
            message = f"✅ Clarity achieved: {clarity*100:.0f}%\n\nI understand your project. Ready to proceed?"
        else:
            status = "partial"
            message = f"⚠️ Clarity: {clarity*100:.0f}% (target: 90%)\n\nLet me ask a few more questions to reach 90% clarity."
        
        return {
            "phase": ClarityPhase.VALIDATION.value,
            "status": status,
            "message": message,
            "summary": summary,
            "clarity_score": clarity,
            "confirmation_needed": True,
            "options": ["Yes, proceed with this plan", "No, I need to clarify something"]
        }
    
    def _generate_summary(self) -> str:
        """Generate a structured summary of the project."""
        summary = "## Project Summary\n\n"
        
        if self.requirements.core_problem:
            summary += f"**Problem**: {self.requirements.core_problem}\n\n"
        
        if self.requirements.target_users:
            summary += f"**Target Users**: {self.requirements.target_users}\n\n"
        
        if self.requirements.key_features:
            summary += f"**Key Features**:\n"
            for feature in self.requirements.key_features:
                summary += f"- {feature}\n"
            summary += "\n"
        
        if self.requirements.success_metrics:
            summary += f"**Success Metrics**:\n"
            for metric in self.requirements.success_metrics:
                summary += f"- {metric}\n"
            summary += "\n"
        
        if self.requirements.timeline:
            summary += f"**Timeline**: {self.requirements.timeline}\n\n"
        
        if self.requirements.technical_constraints:
            summary += f"**Technical Constraints**: {self.requirements.technical_constraints}\n\n"
        
        if self.requirements.integrations:
            summary += f"**Integrations**: {', '.join(self.requirements.integrations)}\n\n"
        
        return summary
    
    def confirm_and_proceed(self, confirmation: bool) -> Dict:
        """
        User confirms or rejects the summary.
        If confirmed, return requirements for orchestrator.
        """
        if confirmation:
            self.current_phase = ClarityPhase.COMPLETE
            return {
                "status": "complete",
                "message": "Perfect! I'm starting the project execution now.",
                "requirements": asdict(self.requirements),
                "clarity_score": self.requirements.clarity_score()
            }
        else:
            self.current_phase = ClarityPhase.INITIAL
            return {
                "status": "restart",
                "message": "No problem. Let's start over. What's your project idea?",
                "requirements": None
            }
    
    def get_state(self) -> Dict:
        """Get current state of ideation process."""
        return {
            "phase": self.current_phase.value,
            "questions_asked": self.questions_asked,
            "clarity_score": self.requirements.clarity_score(),
            "requirements": asdict(self.requirements)
        }

# Example usage
if __name__ == "__main__":
    agent = IdeationAgent()
    
    # Start ideation
    response = agent.start_ideation("I want to build a SaaS platform for URL monitoring")
    print(json.dumps(response, indent=2))
    
    # Simulate user answers
    answers = [
        "Monitor website uptime and performance in real-time",
        "DevOps teams and website owners",
        "Real-time monitoring, Email alerts, Dashboard",
        "99.9% detection accuracy, Sub-minute alert time",
        "3 months MVP, 6 months full launch"
    ]
    
    for i, answer in enumerate(answers):
        response = agent.process_answer(answer, i)
        print(f"\nAnswer {i+1}:")
        print(json.dumps(response, indent=2))
