"""
Sample historical loan cases for the Qdrant database
"""

SAMPLE_LOAN_CASES = [
    # Excellent cases (Grade A)
    {
        "id": "LC-000-GOLD",
        "applicant_profile": "Senior software engineer at tech company, 10 years experience, stable income $8,000/month",
        "loan_amount": 100000,
        "status": "Repaid",
        "grade": "A",
        "dti": 2.1,
        "credit_score": 820,
        "employment_status": "employed",
        "repayment_behavior": "Perfect payment history. No late payments over 60 months. Early payoff.",
        "key_risk_factors": [],
        "category": "High-Value Institutional",
        "region": "California"
    },
    {
        "id": "LC-8271",
        "applicant_profile": "Marketing manager, 5 years same company, monthly income $5,500",
        "loan_amount": 15000,
        "status": "Repaid",
        "grade": "A",
        "dti": 12.5,
        "credit_score": 780,
        "employment_status": "employed",
        "repayment_behavior": "Consistent on-time payments. No issues throughout term.",
        "key_risk_factors": [],
        "category": "Standard Retail",
        "region": "New York"
    },
    
    # Good cases (Grade B)
    {
        "id": "LC-4412",
        "applicant_profile": "Retail store manager, 3 years tenure, income $4,200/month",
        "loan_amount": 12000,
        "status": "Repaid",
        "grade": "B",
        "dti": 18.2,
        "credit_score": 720,
        "employment_status": "employed",
        "repayment_behavior": "Standard payment pattern. Two late payments (30 days) but recovered.",
        "key_risk_factors": ["Brief payment delays"],
        "category": "Standard Retail",
        "region": "Texas"
    },
    {
        "id": "LC-5523",
        "applicant_profile": "Teacher, 8 years experience, stable public sector job, $4,800/month",
        "loan_amount": 20000,
        "status": "Repaid",
        "grade": "B",
        "dti": 22.3,
        "credit_score": 710,
        "employment_status": "employed",
        "repayment_behavior": "Steady payments. One late payment in month 24.",
        "key_risk_factors": ["Single late payment"],
        "category": "Standard Retail",
        "region": "Illinois"
    },
    
    # Moderate risk (Grade C)
    {
        "id": "LC-9921",
        "applicant_profile": "Sales representative, 2 years current job, income $3,800/month with variable commission",
        "loan_amount": 25000,
        "status": "Defaulted",
        "grade": "C",
        "dti": 32.1,
        "credit_score": 650,
        "employment_status": "employed",
        "repayment_behavior": "Started well, missed payments after month 14. Income instability led to default.",
        "key_risk_factors": ["High DTI", "Variable income", "Short employment tenure"],
        "category": "Standard Retail",
        "region": "Florida"
    },
    {
        "id": "LC-3341",
        "applicant_profile": "Freelance graphic designer, 4 years self-employed, avg $3,500/month",
        "loan_amount": 18000,
        "status": "Repaid",
        "grade": "C",
        "dti": 28.5,
        "credit_score": 680,
        "employment_status": "self-employed",
        "repayment_behavior": "Irregular payment schedule due to income volatility, but completed full term.",
        "key_risk_factors": ["Self-employed income volatility", "Multiple late payments"],
        "category": "SME/Entrepreneur",
        "region": "California"
    },
    
    # Higher risk (Grade D)
    {
        "id": "LC-1109",
        "applicant_profile": "Small business owner, restaurant, 1.5 years in business, income $4,500/month",
        "loan_amount": 50000,
        "status": "Defaulted",
        "grade": "D",
        "dti": 41.5,
        "credit_score": 620,
        "employment_status": "self-employed",
        "repayment_behavior": "High debt loading in SME category. Business closure after 18 months led to default.",
        "key_risk_factors": ["High DTI", "New business", "Industry risk", "Excessive debt load"],
        "category": "SME/Entrepreneur",
        "region": "Texas"
    },
    {
        "id": "LC-7788",
        "applicant_profile": "Gig economy worker, multiple income sources, avg $3,200/month",
        "loan_amount": 8000,
        "status": "Defaulted",
        "grade": "D",
        "dti": 38.7,
        "credit_score": 610,
        "employment_status": "self-employed",
        "repayment_behavior": "Inconsistent payments from start. Defaulted after 8 months.",
        "key_risk_factors": ["Unstable income", "High DTI", "Low credit score"],
        "category": "Standard Retail",
        "region": "California"
    },
    
    # High risk (Grade E)
    {
        "id": "LC-2234",
        "applicant_profile": "Recent college graduate, entry-level job, 6 months tenure, $2,800/month",
        "loan_amount": 15000,
        "status": "Defaulted",
        "grade": "E",
        "dti": 45.2,
        "credit_score": 580,
        "employment_status": "employed",
        "repayment_behavior": "Immediate payment struggles. Job loss at month 4. Defaulted quickly.",
        "key_risk_factors": ["Very high DTI", "Short employment", "Low income", "Recent graduate"],
        "category": "Educational/Retail",
        "region": "New York"
    },
    
    # More diverse cases
    {
        "id": "LC-5566",
        "applicant_profile": "Medical professional, doctor, 7 years experience, $12,000/month income",
        "loan_amount": 80000,
        "status": "Repaid",
        "grade": "A",
        "dti": 15.2,
        "credit_score": 790,
        "employment_status": "employed",
        "repayment_behavior": "Excellent payment history. Paid off 2 years early.",
        "key_risk_factors": [],
        "category": "High-Value Institutional",
        "region": "Massachusetts"
    },
    {
        "id": "LC-9988",
        "applicant_profile": "Construction worker, seasonal employment, 5 years experience, avg $3,600/month",
        "loan_amount": 10000,
        "status": "Repaid",
        "grade": "C",
        "dti": 25.8,
        "credit_score": 670,
        "employment_status": "employed",
        "repayment_behavior": "Payment delays during off-season, but completed full term.",
        "key_risk_factors": ["Seasonal income volatility"],
        "category": "Standard Retail",
        "region": "Colorado"
    },
    {
        "id": "LC-4455",
        "applicant_profile": "E-commerce entrepreneur, 2 years in business, growing revenue, $5,200/month",
        "loan_amount": 35000,
        "status": "Repaid",
        "grade": "B",
        "dti": 19.8,
        "credit_score": 730,
        "employment_status": "self-employed",
        "repayment_behavior": "Strong payment pattern. Business growth supported repayment.",
        "key_risk_factors": [],
        "category": "SME/Entrepreneur",
        "region": "Washington"
    },
    {
        "id": "LC-7722",
        "applicant_profile": "Student loan refinance, graduate degree holder, $6,500/month income",
        "loan_amount": 45000,
        "status": "Repaid",
        "grade": "B",
        "dti": 31.2,
        "credit_score": 700,
        "employment_status": "employed",
        "repayment_behavior": "Consistent payments throughout. Lower interest rate helped.",
        "key_risk_factors": ["High existing student debt"],
        "category": "Educational/Retail",
        "region": "California"
    },
    {
        "id": "LC-3399",
        "applicant_profile": "Nurse, healthcare worker, 6 years experience, $5,800/month",
        "loan_amount": 22000,
        "status": "Repaid",
        "grade": "A",
        "dti": 16.5,
        "credit_score": 760,
        "employment_status": "employed",
        "repayment_behavior": "Perfect record. No issues.",
        "key_risk_factors": [],
        "category": "Standard Retail",
        "region": "Florida"
    },
    {
        "id": "LC-8844",
        "applicant_profile": "Uber/Lyft driver, full-time gig work, 1 year, avg $3,400/month",
        "loan_amount": 7500,
        "status": "Defaulted",
        "grade": "D",
        "dti": 42.1,
        "credit_score": 600,
        "employment_status": "self-employed",
        "repayment_behavior": "Very inconsistent. Vehicle issues and platform changes led to default.",
        "key_risk_factors": ["Platform dependency", "High DTI", "Vehicle dependency"],
        "category": "Standard Retail",
        "region": "Texas"
    },
    {
        "id": "LC-1122",
        "applicant_profile": "Corporate manager, Fortune 500 company, 12 years tenure, $9,500/month",
        "loan_amount": 60000,
        "status": "Repaid",
        "grade": "A",
        "dti": 8.5,
        "credit_score": 810,
        "employment_status": "employed",
        "repayment_behavior": "Exemplary. Automated payments, never missed.",
        "key_risk_factors": [],
        "category": "High-Value Institutional",
        "region": "New York"
    },
    {
        "id": "LC-6655",
        "applicant_profile": "Retail manager, 4 years same company, $4,500/month",
        "loan_amount": 14000,
        "status": "Repaid",
        "grade": "B",
        "dti": 24.7,
        "credit_score": 715,
        "employment_status": "employed",
        "repayment_behavior": "Occasional late payments (60 days max) but completed.",
        "key_risk_factors": ["Several late payments"],
        "category": "Standard Retail",
        "region": "Ohio"
    },
    {
        "id": "LC-9955",
        "applicant_profile": "Consultant, contract work, 3 years freelancing, avg $7,200/month",
        "loan_amount": 30000,
        "status": "Repaid",
        "grade": "B",
        "dti": 20.1,
        "credit_score": 740,
        "employment_status": "self-employed",
        "repayment_behavior": "Good payment discipline despite irregular income.",
        "key_risk_factors": ["Contract-based income"],
        "category": "SME/Entrepreneur",
        "region": "California"
    },
    {
        "id": "LC-3377",
        "applicant_profile": "Warehouse worker, 2 years tenure, overtime dependent, $3,300/month base",
        "loan_amount": 9000,
        "status": "Defaulted",
        "grade": "D",
        "dti": 39.8,
        "credit_score": 625,
        "employment_status": "employed",
        "repayment_behavior": "Overtime reduction caused payment failures. Defaulted month 11.",
        "key_risk_factors": ["Overtime dependency", "High DTI", "Income vulnerability"],
        "category": "Standard Retail",
        "region": "Michigan"
    }
]
