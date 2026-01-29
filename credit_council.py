from typing import List, Dict, Any
import os
from models import (
    LoanApplication, 
    CouncilDecision, 
    AgentOpinion, 
    HistoricalCase,
    ConfidenceBreakdown
)
from qdrant_service import QdrantLoanDatabase
from agents import HistorianAgent, AuditorAgent, ComplianceAgent
from anthropic import Anthropic
import json


class CreditCouncil:
    """
    AI Credit Decision Council
    Coordinates multiple agents to make loan decisions using Qdrant for historical data
    """
    
    def __init__(self, api_key: str = None, qdrant_db: QdrantLoanDatabase = None):
        print("\n" + "="*70)
        print("🏛️  INITIALIZING AI CREDIT COUNCIL")
        print("="*70)
        
        # Use existing Qdrant database instance
        if qdrant_db is None:
            raise ValueError("❌ QdrantLoanDatabase instance is required!")
        self.qdrant_db = qdrant_db
        
        # Initialize agents
        print("\n👥 Initializing council members...")
        self.historian = HistorianAgent(api_key=api_key)
        print("  ✅ Historian Agent ready")
        
        self.auditor = AuditorAgent(api_key=api_key)
        print("  ✅ Auditor Agent ready")
        
        self.compliance = ComplianceAgent(api_key=api_key)
        print("  ✅ Compliance Officer ready")
        
        # Initialize coordinator (Claude for final synthesis)
        api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.coordinator = Anthropic(api_key=api_key)
        print("  ✅ Council Coordinator ready")
        
        print("\n✅ Credit Council fully initialized!\n")
    
    def evaluate_application(self, application: LoanApplication) -> CouncilDecision:
        """
        Main method: Evaluate a loan application
        
        Process:
        1. Search Qdrant for similar historical cases
        2. Each agent analyzes the application
        3. Coordinator synthesizes final decision
        """
        print("\n" + "="*70)
        print(f"📋 EVALUATING LOAN APPLICATION: {application.applicant_name}")
        print("="*70)
        
        # Step 1: Determine category for filtering
        category = self._determine_category(application)
        region = self._extract_region(application.business_location)
        
        print(f"\n📊 Application Category: {category}")
        print(f"🌍 Region: {region}")
        print(f"💰 Amount: ${application.amount:,.2f}")
        print(f"📈 DTI Ratio: {application.dti_ratio:.1f}%")
        print(f"⭐ Credit Score: {application.credit_score}")
        
        # Step 2: Search Qdrant for similar cases
        print("\n" + "-"*70)
        print("🔍 PHASE 1: SEARCHING QDRANT FOR HISTORICAL PRECEDENTS")
        print("-"*70)
        
        application_dict = application.model_dump()
        historical_cases = self.qdrant_db.search_similar_cases(
            application=application_dict,
            limit=9,
            category_filter=category,
            region_filter=region
        )
        
        # Display top matches
        print("\n📚 Top 3 Similar Cases:")
        for i, case in enumerate(historical_cases[:3], 1):
            print(f"  {i}. ID: {case['id']} | Similarity: {case['similarity']:.2%} | Status: {case['status']} | Grade: {case['grade']}")
        
        # Step 3: Agent deliberation
        print("\n" + "-"*70)
        print("💬 PHASE 2: AGENT COUNCIL DELIBERATION")
        print("-"*70)
        
        opinions: List[AgentOpinion] = []
        
        # Historian's analysis
        historian_opinion = self.historian.analyze(application, historical_cases)
        opinions.append(historian_opinion)
        print(f"\n📚 Historian ({historian_opinion.agent_name}):")
        print(f"   Vote: {historian_opinion.vote} | Confidence: {historian_opinion.confidence:.0f}%")
        print(f"   Opinion: {historian_opinion.opinion[:150]}...")
        
        # Auditor's analysis
        auditor_opinion = self.auditor.analyze(application, historical_cases)
        opinions.append(auditor_opinion)
        print(f"\n🔍 Auditor ({auditor_opinion.agent_name}):")
        print(f"   Vote: {auditor_opinion.vote} | Confidence: {auditor_opinion.confidence:.0f}%")
        print(f"   Opinion: {auditor_opinion.opinion[:150]}...")
        
        # Compliance analysis
        compliance_opinion = self.compliance.analyze(application, historical_cases)
        opinions.append(compliance_opinion)
        print(f"\n⚖️ Compliance ({compliance_opinion.agent_name}):")
        print(f"   Vote: {compliance_opinion.vote} | Confidence: {compliance_opinion.confidence:.0f}%")
        print(f"   Opinion: {compliance_opinion.opinion[:150]}...")
        
        # Step 4: Coordinator synthesis
        print("\n" + "-"*70)
        print("🎯 PHASE 3: FINAL DECISION SYNTHESIS")
        print("-"*70)
        
        final_decision = self._synthesize_decision(
            application=application,
            opinions=opinions,
            historical_cases=historical_cases
        )
        
        print(f"\n🏛️ FINAL DECISION: {final_decision.final_status}")
        print(f"📊 Confidence Score: {final_decision.confidence_score:.1f}%")
        print(f"⚠️ Risk Score: {final_decision.risk_score:.1f}%")
        print("\n" + "="*70 + "\n")
        
        return final_decision
    
    def _determine_category(self, application: LoanApplication) -> str:
        """Determine loan category for filtering"""
        if application.employment_status.value == 'self-employed':
            return 'SME/Entrepreneur'
        elif application.employment_status.value == 'student':
            return 'Educational/Retail'
        elif application.amount > 100000:
            return 'High-Value Institutional'
        else:
            return 'Standard Retail'
    
    def _extract_region(self, location: str = None) -> str:
        """Extract region from business location"""
        if not location:
            return 'Global'
        # Simple extraction - in production, use proper geocoding
        parts = location.split(',')
        return parts[-1].strip() if len(parts) > 1 else 'Global'
    
    def _synthesize_decision(
        self,
        application: LoanApplication,
        opinions: List[AgentOpinion],
        historical_cases: List[Dict[str, Any]]
    ) -> CouncilDecision:
        """Synthesize final decision from all agents"""
        
        print("\n🤖 Coordinator synthesizing final decision...")
        
        # Prepare context for coordinator
        votes_summary = self._summarize_votes(opinions)
        historical_summary = self._format_historical_for_decision(historical_cases)
        
        prompt = f"""You are the Council Coordinator for a credit decision council.

LOAN APPLICATION:
- Applicant: {application.applicant_name}
- Amount: ${application.amount:,.2f}
- DTI Ratio: {application.dti_ratio:.1f}%
- Credit Score: {application.credit_score}
- Purpose: {application.purpose}

AGENT OPINIONS:
{self._format_opinions(opinions)}

VOTING SUMMARY:
{votes_summary}

HISTORICAL DATA:
{len(historical_cases)} similar cases analyzed from Qdrant vector database.
- Repaid cases: {sum(1 for c in historical_cases if c['status'] == 'Repaid')}
- Defaulted cases: {sum(1 for c in historical_cases if c['status'] == 'Defaulted')}
- Average similarity: {sum(c['similarity'] for c in historical_cases) / len(historical_cases):.2%}

YOUR TASK:
Synthesize a final decision considering:
1. Agent consensus and disagreements
2. Historical precedent patterns from Qdrant
3. Overall risk vs. confidence balance

Respond in this EXACT JSON format:
{{
    "final_status": "Approved" or "Rejected" or "Requires Human Review",
    "summary": "Executive summary of decision in 2-3 sentences",
    "confidence_score": <0-100>,
    "risk_score": <0-100>,
    "confidence_breakdown": {{
        "consensus": <0-100 based on agent agreement>,
        "similarity": <0-100 based on historical match quality>,
        "stability": <0-100 based on consistency of risk factors>
    }},
    "rationale": "Detailed explanation"
}}
"""
        
        response = self.coordinator.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            parsed = json.loads(response.content[0].text)
            
            # Convert historical cases to HistoricalCase models
            historical_precedents = [
                HistoricalCase(
                    id=case['id'],
                    similarity=case['similarity'],
                    status=case['status'],
                    rationale=f"Grade {case['grade']} loan with DTI {case['dti']:.1f}%. {case['repayment_behavior']}",
                    loan_amount=case['loan_amount'],
                    applicant_profile=case['applicant_profile'],
                    key_risk_factors=case.get('key_risk_factors', []),
                    repayment_behavior=case['repayment_behavior']
                )
                for case in historical_cases[:9]
            ]
            
            return CouncilDecision(
                final_status=parsed['final_status'],
                summary=parsed['summary'],
                opinions=opinions,
                historical_precedents=historical_precedents,
                confidence_score=float(parsed['confidence_score']),
                risk_score=float(parsed['risk_score']),
                confidence_breakdown=ConfidenceBreakdown(**parsed['confidence_breakdown'])
            )
            
        except Exception as e:
            print(f"⚠️ Error parsing coordinator response: {e}")
            # Fallback decision
            return self._create_fallback_decision(opinions, historical_cases)
    
    def _summarize_votes(self, opinions: List[AgentOpinion]) -> str:
        """Summarize voting results"""
        approve = sum(1 for o in opinions if o.vote == 'Approve')
        reject = sum(1 for o in opinions if o.vote == 'Reject')
        escalate = sum(1 for o in opinions if o.vote == 'Escalate')
        
        return f"Approve: {approve} | Reject: {reject} | Escalate: {escalate}"
    
    def _format_opinions(self, opinions: List[AgentOpinion]) -> str:
        """Format opinions for prompt"""
        formatted = []
        for op in opinions:
            formatted.append(f"""
{op.role} - {op.agent_name}:
  Vote: {op.vote}
  Confidence: {op.confidence:.0f}%
  Opinion: {op.opinion}
""")
        return "\n".join(formatted)
    
    def _format_historical_for_decision(self, cases: List[Dict[str, Any]]) -> str:
        """Format historical cases summary"""
        if not cases:
            return "No historical cases found."
        
        repaid = sum(1 for c in cases if c['status'] == 'Repaid')
        defaulted = sum(1 for c in cases if c['status'] == 'Defaulted')
        avg_similarity = sum(c['similarity'] for c in cases) / len(cases)
        
        return f"Analyzed {len(cases)} cases: {repaid} Repaid, {defaulted} Defaulted. Avg similarity: {avg_similarity:.2%}"
    
    def _create_fallback_decision(
        self, 
        opinions: List[AgentOpinion], 
        historical_cases: List[Dict[str, Any]]
    ) -> CouncilDecision:
        """Create a fallback decision if synthesis fails"""
        
        approve_votes = sum(1 for o in opinions if o.vote == 'Approve')
        reject_votes = sum(1 for o in opinions if o.vote == 'Reject')
        
        if approve_votes > reject_votes:
            status = 'Approved'
        elif reject_votes > approve_votes:
            status = 'Rejected'
        else:
            status = 'Requires Human Review'
        
        historical_precedents = [
            HistoricalCase(
                id=case['id'],
                similarity=case['similarity'],
                status=case['status'],
                rationale=f"Grade {case['grade']} loan",
                loan_amount=case['loan_amount'],
                applicant_profile=case['applicant_profile'],
                key_risk_factors=case.get('key_risk_factors', []),
                repayment_behavior=case['repayment_behavior']
            )
            for case in historical_cases[:9]
        ]
        
        return CouncilDecision(
            final_status=status,
            summary="Decision made by majority vote of council members.",
            opinions=opinions,
            historical_precedents=historical_precedents,
            confidence_score=60.0,
            risk_score=50.0,
            confidence_breakdown=ConfidenceBreakdown(
                consensus=60.0,
                similarity=70.0,
                stability=65.0
            )
        )
