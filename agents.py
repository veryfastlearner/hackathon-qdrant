from anthropic import Anthropic
import os
from typing import List, Dict, Any
from models import AgentOpinion, LoanApplication
import json


class CreditAgent:
    """Base class for credit decision agents"""
    
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("❌ No API key found! Set ANTHROPIC_API_KEY in .env file")
        self.llm = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def _call_claude(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call Claude API"""
        response = self.llm.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text


class HistorianAgent(CreditAgent):
    """
    The Historian Agent analyzes historical precedents from Qdrant
    Focus: Pattern recognition from similar past cases
    """
    
    SYSTEM_PROMPT = """You are the Lead Historian in a credit decision council.
    
Your role is to analyze historical loan cases retrieved from our vector database (Qdrant).
You look for patterns in:
- Loan grades (A-E) and their correlation with repayment
- DTI (Debt-to-Income) ratios in similar profiles
- How similar applicants performed historically
- Regional and categorical patterns

You provide data-driven insights based on historical precedents.
Be specific about which historical cases support your opinion.
"""
    
    def analyze(
        self, 
        application: LoanApplication, 
        historical_cases: List[Dict[str, Any]]
    ) -> AgentOpinion:
        """Analyze application based on historical cases"""
        
        print("📚 Historian Agent analyzing...")
        
        # Prepare historical context
        cases_summary = self._format_cases(historical_cases)
        
        prompt = f"""{self.SYSTEM_PROMPT}

CURRENT APPLICATION:
- Applicant: {application.applicant_name}
- Amount: ${application.amount:,.2f}
- Purpose: {application.purpose}
- Monthly Income: ${application.monthly_income:,.2f}
- Existing Debt: ${application.existing_debt:,.2f}
- DTI Ratio: {application.dti_ratio:.1f}%
- Credit Score: {application.credit_score}
- Employment: {application.employment_status.value}
- Employment Years: {application.employment_years}
- Location: {application.business_location or 'Not specified'}

HISTORICAL CASES FROM QDRANT (Ranked by similarity):
{cases_summary}

Analyze these historical precedents and provide your opinion.
You must respond in this EXACT JSON format:
{{
    "opinion": "Your detailed analysis in 2-3 sentences",
    "vote": "Approve" or "Reject" or "Escalate",
    "confidence": <number between 0-100>,
    "key_findings": "Summary of most relevant patterns from history"
}}
"""
        
        response = self._call_claude(prompt, max_tokens=800)
        
        try:
            parsed = json.loads(response)
            return AgentOpinion(
                agent_name="Dr. Sarah Chen",
                role="Historian",
                opinion=parsed.get("opinion", response[:200]),
                vote=parsed.get("vote", "Escalate"),
                confidence=float(parsed.get("confidence", 50))
            )
        except:
            # Fallback if JSON parsing fails
            return AgentOpinion(
                agent_name="Dr. Sarah Chen",
                role="Historian",
                opinion=response[:300],
                vote="Escalate",
                confidence=50.0
            )
    
    def _format_cases(self, cases: List[Dict[str, Any]]) -> str:
        """Format historical cases for prompt"""
        formatted = []
        for i, case in enumerate(cases[:9], 1):  # Top 9 cases
            formatted.append(f"""
Case #{i} (Similarity: {case.get('similarity', 0):.2%}):
- ID: {case.get('id', 'Unknown')}
- Amount: ${case.get('loan_amount', 0):,.2f}
- Grade: {case.get('grade', 'Unknown')}
- DTI: {case.get('dti', 0):.1f}%
- Status: {case.get('status', 'Unknown')}
- Profile: {case.get('applicant_profile', 'N/A')}
- Behavior: {case.get('repayment_behavior', 'N/A')}
- Risk Factors: {', '.join(case.get('key_risk_factors', []))}
""")
        return "\n".join(formatted)


class AuditorAgent(CreditAgent):
    """
    The Financial Risk Auditor
    Focus: Financial metrics and risk assessment
    """
    
    SYSTEM_PROMPT = """You are the Financial Risk Auditor in a credit decision council.

Your role is to challenge and scrutinize the financial metrics:
- DTI (Debt-to-Income) ratio - Flag if > 40% as high risk
- Income stability and employment tenure
- Loan amount relative to income
- Credit score appropriateness
- Purpose of loan and its risk profile

You are the skeptic who prevents bad loans. Be thorough and critical.
"""
    
    def analyze(
        self, 
        application: LoanApplication, 
        historical_cases: List[Dict[str, Any]]
    ) -> AgentOpinion:
        """Analyze application from risk perspective"""
        
        print("🔍 Auditor Agent analyzing...")
        
        # Calculate key metrics
        dti = application.dti_ratio
        income_to_loan = (application.amount / (application.monthly_income * 12)) if application.monthly_income > 0 else 999
        
        prompt = f"""{self.SYSTEM_PROMPT}

CURRENT APPLICATION METRICS:
- Applicant: {application.applicant_name}
- Requested Amount: ${application.amount:,.2f}
- Monthly Income: ${application.monthly_income:,.2f}
- Annual Income: ${application.monthly_income * 12:,.2f}
- Existing Monthly Debt: ${application.existing_debt:,.2f}
- DTI Ratio: {dti:.1f}% {'⚠️ HIGH RISK' if dti > 40 else '✓ Acceptable'}
- Loan-to-Annual-Income Ratio: {income_to_loan:.1%}
- Credit Score: {application.credit_score} {'⚠️ Poor' if application.credit_score < 600 else '✓ Good' if application.credit_score > 700 else 'Fair'}
- Employment: {application.employment_status.value}
- Employment Tenure: {application.employment_years} years
- Purpose: {application.purpose}

RISK ASSESSMENT GUIDELINES:
- DTI > 40%: High risk
- DTI 30-40%: Moderate risk
- DTI < 30%: Low risk
- Credit Score < 600: High risk
- Employment < 2 years: Higher risk
- Loan > 3x annual income: High risk

Provide your financial risk assessment.
Respond in this EXACT JSON format:
{{
    "opinion": "Your risk analysis in 2-3 sentences",
    "vote": "Approve" or "Reject" or "Escalate",
    "confidence": <number between 0-100>,
    "key_concerns": "Main financial red flags or green lights"
}}
"""
        
        response = self._call_claude(prompt, max_tokens=800)
        
        try:
            parsed = json.loads(response)
            return AgentOpinion(
                agent_name="Michael Rodriguez",
                role="Auditor",
                opinion=parsed.get("opinion", response[:200]),
                vote=parsed.get("vote", "Escalate"),
                confidence=float(parsed.get("confidence", 50))
            )
        except:
            return AgentOpinion(
                agent_name="Michael Rodriguez",
                role="Auditor",
                opinion=response[:300],
                vote="Escalate",
                confidence=50.0
            )


class ComplianceAgent(CreditAgent):
    """
    The Compliance Officer
    Focus: Regulatory compliance, fraud detection, ethical lending
    """
    
    SYSTEM_PROMPT = """You are the Compliance Officer in a credit decision council.

Your role is to ensure:
- Regulatory compliance and fair lending practices
- Detection of "loan flipping" or predatory patterns
- Purpose legitimacy and consistency with employment
- AML (Anti-Money Laundering) red flags
- Jurisdictional issues
- Ethical lending standards

You protect both the institution and the borrower from problematic loans.
"""
    
    def analyze(
        self, 
        application: LoanApplication, 
        historical_cases: List[Dict[str, Any]]
    ) -> AgentOpinion:
        """Analyze application from compliance perspective"""
        
        print("⚖️ Compliance Officer analyzing...")
        
        prompt = f"""{self.SYSTEM_PROMPT}

CURRENT APPLICATION:
- Applicant: {application.applicant_name}
- Amount: ${application.amount:,.2f}
- Purpose: {application.purpose}
- Employment: {application.employment_status.value}
- Employment Tenure: {application.employment_years} years
- Location: {application.business_location or 'Not specified'}
- Credit Score: {application.credit_score}

COMPLIANCE CHECKS:
1. Purpose Legitimacy: Does the stated purpose align with employment and profile?
2. Loan Flipping Risk: Is the amount or pattern suspicious?
3. Employment Consistency: Does employment tenure support the loan purpose?
4. Geographic/Jurisdictional Factors: Any regional compliance issues?
5. Fair Lending: Any discriminatory or predatory indicators?

Provide your compliance assessment.
Respond in this EXACT JSON format:
{{
    "opinion": "Your compliance analysis in 2-3 sentences",
    "vote": "Approve" or "Reject" or "Escalate",
    "confidence": <number between 0-100>,
    "compliance_flags": "Any red flags or clearances"
}}
"""
        
        response = self._call_claude(prompt, max_tokens=800)
        
        try:
            parsed = json.loads(response)
            return AgentOpinion(
                agent_name="Lisa Wong",
                role="Compliance",
                opinion=parsed.get("opinion", response[:200]),
                vote=parsed.get("vote", "Escalate"),
                confidence=float(parsed.get("confidence", 50))
            )
        except:
            return AgentOpinion(
                agent_name="Lisa Wong",
                role="Compliance",
                opinion=response[:300],
                vote="Escalate",
                confidence=50.0
            )
