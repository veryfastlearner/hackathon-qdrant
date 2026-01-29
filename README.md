# 🏛️ AI Credit Council - Qdrant Powered

A sophisticated multi-agent credit decision system using **Qdrant vector database** for intelligent historical case retrieval and **Claude AI** for agent reasoning.

## 🎯 Overview

This system recreates your original AI Studio credit council but with **real vector search** using Qdrant instead of simulation. It features:

- **3 Specialized AI Agents**: Historian, Auditor, and Compliance Officer
- **Qdrant Vector Database**: Stores and searches 20+ historical loan cases using semantic similarity
- **Multi-Agent Deliberation**: Agents debate and vote on loan applications
- **Confidence Scoring**: Detailed breakdown of decision confidence
- **Historical Precedent Analysis**: Finds similar past cases to inform decisions

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LOAN APPLICATION                          │
│   (Applicant data, income, credit score, purpose, etc.)     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              QDRANT VECTOR SEARCH                            │
│  • Embeds application using sentence-transformers           │
│  • Searches 384-dimensional vector space                    │
│  • Filters by category and region                           │
│  • Returns top 9 similar historical cases                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              AGENT COUNCIL DELIBERATION                      │
│                                                              │
│  📚 HISTORIAN AGENT (Dr. Sarah Chen)                        │
│     • Analyzes historical precedents from Qdrant           │
│     • Identifies patterns in similar cases                  │
│     • Correlates loan grades with repayment                 │
│                                                              │
│  🔍 AUDITOR AGENT (Michael Rodriguez)                       │
│     • Evaluates financial metrics (DTI, income)            │
│     • Challenges risky applications                         │
│     • Flags high-risk indicators                            │
│                                                              │
│  ⚖️ COMPLIANCE AGENT (Lisa Wong)                           │
│     • Ensures regulatory compliance                         │
│     • Detects fraud patterns                                │
│     • Validates legitimacy and ethics                       │
│                                                              │
│  Each agent provides:                                        │
│  - Opinion (detailed analysis)                               │
│  - Vote (Approve/Reject/Escalate)                           │
│  - Confidence (0-100%)                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            COORDINATOR SYNTHESIS (Claude)                    │
│  • Weighs all agent opinions                                 │
│  • Analyzes voting consensus                                 │
│  • Considers historical match quality                        │
│  • Produces final decision with confidence breakdown         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  FINAL DECISION                              │
│  • Status: Approved/Rejected/Requires Human Review          │
│  • Confidence Score: Overall certainty (0-100%)             │
│  • Risk Score: Default probability (0-100%)                 │
│  • Agent opinions and votes                                  │
│  • Top 9 historical precedents                               │
│  • Detailed rationale                                        │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8+
- Anthropic API Key ([Get one here](https://console.anthropic.com/))

### Installation

1. **Navigate to the project directory**:
   ```bash
   cd ai_credit_council
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API key**:
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your API key
   # ANTHROPIC_API_KEY=your_actual_key_here
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

## 📊 Features

### 1. Qdrant Vector Database

- **Semantic Search**: Finds similar loan cases based on meaning, not just keywords
- **384-Dimensional Vectors**: Rich representation using sentence-transformers
- **Metadata Filtering**: Filter by category (SME, Retail, Institutional) and region
- **Persistent Storage**: Data saved in `./qdrant_loan_data`

### 2. AI Agents

#### 📚 Historian Agent
- Specializes in pattern recognition from historical data
- References specific Qdrant cases in analysis
- Tracks correlation between loan grades and outcomes

#### 🔍 Auditor Agent
- Financial risk assessment expert
- DTI ratio analysis (flags >40% as high risk)
- Income stability evaluation
- Credit score appropriateness

#### ⚖️ Compliance Officer
- Regulatory compliance monitoring
- Fraud and loan flipping detection
- Purpose legitimacy validation
- Ethical lending standards

### 3. Decision Metrics

- **Confidence Score** (0-100%): Overall decision certainty
- **Risk Score** (0-100%): Probability of default
- **Confidence Breakdown**:
  - Consensus: Agent agreement level
  - Similarity: Quality of historical matches
  - Stability: Consistency of risk factors

## 🎮 Usage

### Main Menu Options

1. **Evaluate Sample Applications**: Test with 3 pre-configured cases
   - Strong applicant (should approve)
   - High risk applicant (should reject)
   - Borderline case (should escalate)

2. **Interactive Mode**: Enter custom loan applications
   - Enter applicant details
   - Get real-time AI council decision

3. **Database Statistics**: View Qdrant database info

### Example Session

```
🏛️  AI CREDIT COUNCIL - QDRANT POWERED
   Multi-Agent Credit Decision System
==================================================

📚 INITIALIZING LOAN DATABASE
✅ Database already initialized with 20 cases

🏛️  INITIALIZING AI CREDIT COUNCIL
👥 Initializing council members...
  ✅ Historian Agent ready
  ✅ Auditor Agent ready
  ✅ Compliance Officer ready
  ✅ Council Coordinator ready

📋 MAIN MENU
1. Evaluate sample applications
2. Enter custom application
3. View database statistics
4. Exit

Choose an option (1-4): 1

EVALUATING LOAN APPLICATION: John Smith
💰 Amount: $25,000.00
📈 DTI Ratio: 12.3%
⭐ Credit Score: 750

🔍 PHASE 1: SEARCHING QDRANT
✅ Found 9 similar cases

💬 PHASE 2: AGENT COUNCIL DELIBERATION

📚 Historian: Vote: Approve | Confidence: 85%
🔍 Auditor: Vote: Approve | Confidence: 90%
⚖️ Compliance: Vote: Approve | Confidence: 88%

🎯 PHASE 3: FINAL DECISION SYNTHESIS

🏛️ FINAL DECISION: Approved
📊 Confidence Score: 87.7%
⚠️ Risk Score: 12.3%
```

## 📁 Project Structure

```
ai_credit_council/
├── models.py              # Pydantic models for data structures
├── qdrant_service.py      # Qdrant database operations
├── agents.py              # AI agent implementations
├── credit_council.py      # Main council orchestrator
├── sample_data.py         # Historical loan cases
├── main.py                # Entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## 🔧 Key Components

### Qdrant Integration

```python
# Search similar cases
similar_cases = qdrant_db.search_similar_cases(
    application=app_data,
    limit=9,
    category_filter="Standard Retail",
    region_filter="California"
)
```

### Agent Evaluation

```python
# Each agent analyzes independently
historian_opinion = historian.analyze(application, historical_cases)
auditor_opinion = auditor.analyze(application, historical_cases)
compliance_opinion = compliance.analyze(application, historical_cases)
```

### Council Decision

```python
# Coordinator synthesizes final decision
decision = council.evaluate_application(application)
# Returns: status, confidence, risk score, opinions, precedents
```

## 📈 Sample Historical Data

The database includes 20 diverse historical cases:

- **Grade A**: Excellent borrowers (e.g., tech workers, doctors)
- **Grade B**: Good borrowers (teachers, managers)
- **Grade C**: Moderate risk (freelancers, sales)
- **Grade D**: Higher risk (new businesses, gig workers)
- **Grade E**: High risk (recent graduates, unstable income)

Cases span various:
- Employment types (employed, self-employed, student)
- Industries (tech, retail, healthcare, gig economy)
- Loan purposes (debt consolidation, business, education)
- Regions (California, Texas, New York, etc.)

## 🎯 Comparison to Original

### Original (AI Studio)
- ✅ Multi-agent council
- ✅ 3 specialized roles
- ✅ Historical precedent simulation
- ❌ Simulated vector search
- ❌ No persistent database

### This Version (Qdrant Powered)
- ✅ Multi-agent council (same roles preserved)
- ✅ 3 specialized agents (Historian, Auditor, Compliance)
- ✅ Real historical precedent search
- ✅ Actual vector similarity (Qdrant)
- ✅ Persistent vector database
- ✅ Semantic search with embeddings
- ✅ Metadata filtering
- ✅ Scalable to thousands of cases

## 🔍 How It Works

1. **Application Submitted**: User provides loan details
2. **Vector Embedding**: Application converted to 384-dim vector
3. **Qdrant Search**: Finds 9 most similar historical cases
4. **Agent Analysis**: Each agent independently evaluates
5. **Council Deliberation**: Agents vote and provide opinions
6. **Synthesis**: Coordinator weighs all inputs
7. **Decision**: Final status with confidence metrics

## 🚀 Advanced Features

### Adding More Historical Data

```python
from qdrant_service import QdrantLoanDatabase

db = QdrantLoanDatabase()

new_cases = [
    {
        "id": "LC-NEW-001",
        "applicant_profile": "Your profile description",
        "loan_amount": 30000,
        "status": "Repaid",
        "grade": "B",
        "dti": 25.5,
        "credit_score": 720,
        "employment_status": "employed",
        "repayment_behavior": "Description",
        "key_risk_factors": ["factor1", "factor2"],
        "category": "Standard Retail",
        "region": "California"
    }
]

db.add_historical_cases(new_cases)
```

### Custom Agent Behavior

Edit `agents.py` to modify agent prompts and logic:

```python
class HistorianAgent(CreditAgent):
    SYSTEM_PROMPT = """Your custom prompt here..."""
```

## 🛠️ Troubleshooting

**Issue**: "No API key found"
- **Solution**: Create `.env` file with `ANTHROPIC_API_KEY=your_key`

**Issue**: Import errors
- **Solution**: Ensure virtual environment is activated and dependencies installed

**Issue**: Qdrant errors
- **Solution**: Delete `./qdrant_loan_data` folder and restart to rebuild

## 📝 License

This project recreates the functionality of your AI Studio application using Qdrant for production-grade vector search.

## 🙏 Acknowledgments

- **Original Design**: AI Studio credit council concept
- **Qdrant**: Vector database for semantic search
- **Anthropic Claude**: Multi-agent reasoning
- **Sentence Transformers**: Text embeddings

---

**Built with ❤️ using Qdrant + Claude AI**
