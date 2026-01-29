#!/usr/bin/env python3
"""
AI Credit Council - Main Application
Multi-agent credit decision system using Qdrant for vector search
"""

from dotenv import load_dotenv
import os
from models import LoanApplication, EmploymentStatus
from credit_council import CreditCouncil
from qdrant_service import QdrantLoanDatabase
from sample_data import SAMPLE_LOAN_CASES

# Load environment variables
load_dotenv()


def initialize_database():
    """Initialize Qdrant with sample historical data"""
    print("\n" + "="*70)
    print("📚 INITIALIZING LOAN DATABASE")
    print("="*70)
    
    db = QdrantLoanDatabase()
    
    # Check if database already has data
    stats = db.get_collection_stats()
    
    if stats.get('total_cases', 0) > 0:
        print(f"\n✅ Database already initialized with {stats['total_cases']} cases")
        return db
    
    # Add sample historical cases
    print(f"\n📥 Adding {len(SAMPLE_LOAN_CASES)} historical loan cases to Qdrant...")
    db.add_historical_cases(SAMPLE_LOAN_CASES)
    
    # Show stats
    stats = db.get_collection_stats()
    print(f"\n📊 Database Statistics:")
    print(f"   Total Cases: {stats.get('total_cases', 0)}")
    print(f"   Vector Size: {stats.get('vector_size', 0)}")
    print(f"   Distance Metric: {stats.get('distance_metric', 'N/A')}")
    
    return db


def create_sample_applications():
    """Create sample loan applications for testing"""
    return [
        # Case 1: Strong applicant - should be approved
        LoanApplication(
            applicant_name="John Smith",
            amount=25000,
            purpose="Debt consolidation",
            monthly_income=6500,
            existing_debt=800,
            credit_score=750,
            employment_status=EmploymentStatus.EMPLOYED,
            employment_years=5,
            business_location="San Francisco, California"
        ),
        
        # Case 2: High risk - should be rejected
        LoanApplication(
            applicant_name="Jane Doe",
            amount=40000,
            purpose="Business startup",
            monthly_income=3200,
            existing_debt=1500,
            credit_score=590,
            employment_status=EmploymentStatus.SELF_EMPLOYED,
            employment_years=0.5,
            business_location="Austin, Texas"
        ),
        
        # Case 3: Borderline - should require human review
        LoanApplication(
            applicant_name="Mike Johnson",
            amount=18000,
            purpose="Home improvement",
            monthly_income=4800,
            existing_debt=1600,
            credit_score=680,
            employment_status=EmploymentStatus.EMPLOYED,
            employment_years=2,
            business_location="Miami, Florida"
        ),
    ]


def display_decision(decision, application):
    """Display the council's decision in a formatted way"""
    print("\n" + "="*70)
    print("🏛️  CREDIT COUNCIL DECISION")
    print("="*70)
    
    print(f"\n📋 Applicant: {application.applicant_name}")
    print(f"💰 Amount: ${application.amount:,.2f}")
    print(f"🎯 Purpose: {application.purpose}")
    
    # Status with emoji
    status_emoji = {
        'Approved': '✅',
        'Rejected': '❌',
        'Requires Human Review': '⚠️'
    }
    
    print(f"\n{status_emoji.get(decision.final_status, '📋')} DECISION: {decision.final_status}")
    print(f"\n📊 Metrics:")
    print(f"   Confidence Score: {decision.confidence_score:.1f}%")
    print(f"   Risk Score: {decision.risk_score:.1f}%")
    
    print(f"\n💡 Confidence Breakdown:")
    print(f"   Consensus: {decision.confidence_breakdown.consensus:.1f}%")
    print(f"   Similarity: {decision.confidence_breakdown.similarity:.1f}%")
    print(f"   Stability: {decision.confidence_breakdown.stability:.1f}%")
    
    print(f"\n📝 Summary:")
    print(f"   {decision.summary}")
    
    print(f"\n👥 Agent Opinions:")
    for opinion in decision.opinions:
        vote_emoji = {'Approve': '✅', 'Reject': '❌', 'Escalate': '⚠️'}
        print(f"\n   {opinion.role} - {opinion.agent_name}:")
        print(f"   {vote_emoji.get(opinion.vote, '📋')} Vote: {opinion.vote} (Confidence: {opinion.confidence:.0f}%)")
        print(f"   Opinion: {opinion.opinion[:200]}...")
    
    print(f"\n📚 Top Historical Precedents:")
    for i, case in enumerate(decision.historical_precedents[:5], 1):
        status_icon = '✅' if case.status == 'Repaid' else '❌'
        print(f"   {i}. {status_icon} {case.id} (Similarity: {case.similarity:.1%})")
        print(f"      Amount: ${case.loan_amount:,.2f} | Status: {case.status}")
        print(f"      Profile: {case.applicant_profile[:80]}...")
    
    print("\n" + "="*70 + "\n")


def interactive_mode(council):
    """Interactive mode for custom loan applications"""
    print("\n" + "="*70)
    print("💬 INTERACTIVE MODE - Enter Loan Application")
    print("="*70)
    
    try:
        name = input("\nApplicant Name: ")
        amount = float(input("Loan Amount ($): "))
        purpose = input("Purpose: ")
        monthly_income = float(input("Monthly Income ($): "))
        existing_debt = float(input("Existing Monthly Debt ($): "))
        credit_score = int(input("Credit Score (300-850): "))
        
        print("\nEmployment Status:")
        print("  1. Employed")
        print("  2. Self-employed")
        print("  3. Unemployed")
        print("  4. Student")
        emp_choice = input("Choose (1-4): ")
        
        emp_map = {
            '1': EmploymentStatus.EMPLOYED,
            '2': EmploymentStatus.SELF_EMPLOYED,
            '3': EmploymentStatus.UNEMPLOYED,
            '4': EmploymentStatus.STUDENT
        }
        employment_status = emp_map.get(emp_choice, EmploymentStatus.EMPLOYED)
        
        employment_years = float(input("Years of Employment: "))
        business_location = input("Location (City, State): ")
        
        # Create application
        application = LoanApplication(
            applicant_name=name,
            amount=amount,
            purpose=purpose,
            monthly_income=monthly_income,
            existing_debt=existing_debt,
            credit_score=credit_score,
            employment_status=employment_status,
            employment_years=employment_years,
            business_location=business_location if business_location else None
        )
        
        # Evaluate
        decision = council.evaluate_application(application)
        
        # Display result
        display_decision(decision, application)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Main application entry point"""
    print("\n" + "="*70)
    print("🏛️  AI CREDIT COUNCIL - QDRANT POWERED")
    print("   Multi-Agent Credit Decision System")
    print("="*70)
    
    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("\n❌ ERROR: ANTHROPIC_API_KEY not found in environment!")
        print("Please create a .env file with your API key:")
        print("   ANTHROPIC_API_KEY=your_key_here")
        return
    
    # Step 1: Initialize database
    db = initialize_database()
    
    # Step 2: Initialize credit council
    council = CreditCouncil(qdrant_db=db)
    
    # Step 3: Main menu
    while True:
        print("\n" + "="*70)
        print("📋 MAIN MENU")
        print("="*70)
        print("\n1. Evaluate sample applications (3 test cases)")
        print("2. Enter custom application (interactive)")
        print("3. View database statistics")
        print("4. Exit")
        
        choice = input("\nChoose an option (1-4): ")
        
        if choice == '1':
            # Evaluate sample applications
            samples = create_sample_applications()
            
            for i, app in enumerate(samples, 1):
                print(f"\n\n{'='*70}")
                print(f"EVALUATING SAMPLE APPLICATION {i}/{len(samples)}")
                print(f"{'='*70}")
                
                decision = council.evaluate_application(app)
                display_decision(decision, app)
                
                if i < len(samples):
                    input("\nPress Enter to continue to next application...")
        
        elif choice == '2':
            # Interactive mode
            interactive_mode(council)
        
        elif choice == '3':
            # Database stats
            stats = db.get_collection_stats()
            print("\n📊 Database Statistics:")
            print(f"   Total Historical Cases: {stats.get('total_cases', 0)}")
            print(f"   Vector Dimension: {stats.get('vector_size', 0)}")
            print(f"   Distance Metric: {stats.get('distance_metric', 'N/A')}")
        
        elif choice == '4':
            print("\n👋 Thank you for using AI Credit Council!")
            break
        
        else:
            print("\n❌ Invalid choice. Please choose 1-4.")


if __name__ == "__main__":
    main()
