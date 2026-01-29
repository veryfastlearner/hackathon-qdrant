from pydantic import BaseModel
from typing import List, Literal, Optional
from enum import Enum


class EmploymentStatus(str, Enum):
    EMPLOYED = "employed"
    SELF_EMPLOYED = "self-employed"
    UNEMPLOYED = "unemployed"
    STUDENT = "student"


class LoanApplication(BaseModel):
    applicant_name: str
    amount: float
    purpose: str
    monthly_income: float
    existing_debt: float
    credit_score: int
    employment_status: EmploymentStatus
    employment_years: float
    business_location: Optional[str] = None

    @property
    def dti_ratio(self) -> float:
        """Calculate Debt-to-Income ratio"""
        if self.monthly_income == 0:
            return 999.0
        return (self.existing_debt / self.monthly_income) * 100


class HistoricalCase(BaseModel):
    id: str
    similarity: float
    status: Literal['Repaid', 'Defaulted']
    rationale: str
    loan_amount: float
    applicant_profile: str
    key_risk_factors: List[str]
    repayment_behavior: str


class AgentOpinion(BaseModel):
    agent_name: str
    role: Literal['Historian', 'Auditor', 'Compliance']
    opinion: str
    vote: Literal['Approve', 'Reject', 'Escalate']
    confidence: float  # 0-100


class ConfidenceBreakdown(BaseModel):
    consensus: float  # Agreement level between agents
    similarity: float  # Quality of historical matches
    stability: float  # Consistency of risk factors


class CouncilDecision(BaseModel):
    final_status: Literal['Approved', 'Rejected', 'Requires Human Review']
    summary: str
    opinions: List[AgentOpinion]
    historical_precedents: List[HistoricalCase]
    confidence_score: float  # 0-100 (Overall Confidence)
    risk_score: float  # 0-100 (Probability of default)
    confidence_breakdown: ConfidenceBreakdown
