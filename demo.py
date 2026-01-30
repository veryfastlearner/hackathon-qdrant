"""
Complete Loan Application Processing Demo
Run this file to see everything in action!
"""

import os
import pandas as pd
import streamlit as st
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from fastembed import TextEmbedding
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize clients
@st.cache_resource
def init_clients():
    qdrant_client = QdrantClient(":memory:")
    embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    GROK_API_KEY = os.getenv("GROK_API_KEY", "").strip()
    if not GROK_API_KEY:
        st.error("GROK_API_KEY not set in environment. Add it to .env file.")
        st.stop()
    
    # Test the API key by creating client
    try:
        grok_client = Groq(api_key=GROK_API_KEY)
        # Test with a simple call to verify key works
        test_response = grok_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "unauthorized" in error_msg.lower() or "invalid" in error_msg.lower() or "expired" in error_msg.lower():
            st.error(f"❌ API Key Error: {error_msg}")
            st.error("Please check your GROK_API_KEY in the .env file. Make sure it's valid and not expired.")
        else:
            st.error(f"Error initializing Groq client: {error_msg}")
        st.stop()
    
    return qdrant_client, embedding_model, grok_client

qdrant_client, embedding_model, grok_client = init_clients()

# LLM Council Members with different personas
COUNCIL_MEMBERS = [
    {
        "name": "Dr. Sarah Chen",
        "role": "Risk Assessment Specialist",
        "persona": "You are Dr. Sarah Chen, a conservative risk assessment specialist with 20 years of experience. You ALWAYS focus on NUMBERS FIRST: credit scores, debt-to-income ratios, payment history, and financial stability. You are skeptical and look for red flags. You reject applications with credit scores below 700, debt-to-income above 35%, or any missed payments. You prioritize protecting the lender's capital. Your analysis is data-driven and you rarely approve risky applications. When you speak, you cite specific numbers and financial metrics."
    },
    {
        "name": "Michael Rodriguez",
        "role": "Growth & Opportunity Analyst",
        "persona": "You are Michael Rodriguez, an optimistic growth analyst who focuses on FUTURE POTENTIAL and OPPORTUNITY. You believe in second chances and look beyond current financial status. You value: entrepreneurial spirit, education investments, career growth potential, and life circumstances. You are willing to approve applications that others might reject if you see growth potential. You focus on what the applicant CAN become, not just their current situation. You often argue for giving people opportunities to improve their lives. You look for positive trends and potential, not just current numbers."
    },
    {
        "name": "Emily Watson",
        "role": "Fair Lending Advocate",
        "persona": "You are Emily Watson, a fair lending advocate who focuses on EQUITY and SOCIAL IMPACT. You look at the FULL CONTEXT: life circumstances, systemic barriers, family needs, and social justice. You consider: medical emergencies, job loss, education access, and underserved communities. You often disagree with purely numbers-based decisions. You advocate for applicants facing hardships or discrimination. You look for reasons to APPROVE when others might reject, especially for marginalized groups. You prioritize human dignity and equal access to credit over strict financial metrics."
    }
]

def setup_qdrant_collection(collection_name: str = "loan_applications"):
    """Set up Qdrant collection."""
    try:
        qdrant_client.get_collection(collection_name)
    except:
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=384,  # bge-small-en-v1.5 embedding size
                distance=Distance.COSINE
            )
        )

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed texts using FastEmbed."""
    embeddings = list(embedding_model.embed(texts))
    return [embed.tolist() for embed in embeddings]

def store_loan_applications_batch(applications: List[Dict[str, str]], collection_name: str = "loan_applications"):
    """Store multiple loan applications in one batch."""
    setup_qdrant_collection(collection_name)
    
    # Embed all texts at once
    texts = [app["text"] for app in applications]
    embeddings = embed_texts(texts)
    
    points = []
    for app, embedding in zip(applications, embeddings):
        points.append(PointStruct(
            id=hash(app["id"]) % (2**63),
            vector=embedding,
            payload={"text": app["text"], "application_id": app["id"]}
        ))
    
    qdrant_client.upsert(collection_name=collection_name, points=points)
    return len(points)

def similarity_search(query_text: str, top_k: int = 5, collection_name: str = "loan_applications") -> List[Dict]:
    """Perform similarity search."""
    try:
        # Check if collection exists and has data
        try:
            collection_info = qdrant_client.get_collection(collection_name)
            count = qdrant_client.count(collection_name=collection_name)
            if count.count == 0:
                return []
        except:
            # Collection doesn't exist
            return []
        
        query_embedding = list(embedding_model.embed([query_text]))[0].tolist()
        
        results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=top_k
        )
        
        return [
            {
                "score": result.score,
                "text": result.payload.get("text", ""),
                "application_id": result.payload.get("application_id", "unknown")
            }
            for result in results
        ]
    except Exception as e:
        # Return empty list on any error
        return []

def llm_council_vote(application_text: str, similar_applications: List[Dict], debate_container=None) -> Dict:
    """LLM council votes with live debate."""
    # Prepare context from similar applications
    if similar_applications:
        similar_context = "\n".join([
            f"Similar application (score: {app['score']:.3f}): {app['text'][:200]}..."
            for app in similar_applications[:3]
        ])
    else:
        similar_context = "No similar applications found in database."
    
    # Create base prompt
    base_context = f"""Review this loan application and similar past applications.

NEW LOAN APPLICATION:
{application_text}

SIMILAR PAST APPLICATIONS:
{similar_context}"""

    # STEP 1: Initial thoughts from each member
    if debate_container:
        debate_container.subheader("💬 Council Debate - Initial Thoughts")
    
    initial_thoughts = []
    for i, member in enumerate(COUNCIL_MEMBERS):
        # Different focus for each member
        focus_prompts = [
            "Analyze the NUMBERS: credit score, income, debt-to-income ratio. What are the financial RISKS? (1-2 sentences)",
            "Look at the POTENTIAL and OPPORTUNITY. What positive aspects or growth potential do you see? (1-2 sentences)",
            "Consider the FULL CONTEXT and LIFE CIRCUMSTANCES. What social or equity factors matter here? (1-2 sentences)"
        ]
        
        initial_prompt = f"{base_context}\n\n{focus_prompts[i]}"
        
        try:
            response = grok_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": member['persona'] + " Think from YOUR unique perspective. Be concise. Maximum 2 sentences. Use your specific lens."},
                    {"role": "user", "content": initial_prompt}
                ],
                temperature=0.9,  # Higher temperature for more diverse responses
                max_tokens=100
            )
            
            thought = response.choices[0].message.content
            initial_thoughts.append({
                "member": member["name"],
                "role": member["role"],
                "thought": thought
            })
            
            if debate_container:
                with debate_container.expander(f"💭 {member['name']} ({member['role']}) - Initial Thoughts"):
                    st.write(thought)
        except Exception as e:
            error_msg = str(e)
            if debate_container:
                st.error(f"Error from {member['name']}: {error_msg}")
            initial_thoughts.append({
                "member": member["name"],
                "role": member["role"],
                "thought": f"Error: {error_msg}"
            })
    
    # STEP 2: Debate round - each member responds to others
    if debate_container:
        debate_container.subheader("🗣️ Council Debate - Discussion Round")
        debate_container.write("Council members are now discussing and responding to each other...")
    
    debate_responses = []
    for i, member in enumerate(COUNCIL_MEMBERS):
        # Get thoughts from other members
        other_thoughts = "\n\n".join([
            f"{t['member']} ({t['role']}) said: {t['thought']}"
            for j, t in enumerate(initial_thoughts) if j != i
        ])
        
        # Different debate angles for each member
        debate_angles = [
            "Challenge them with DATA and NUMBERS. What financial risks are they ignoring?",
            "Argue for OPPORTUNITY and POTENTIAL. What positive aspects are they missing?",
            "Advocate for CONTEXT and EQUITY. What life circumstances are they overlooking?"
        ]
        
        debate_prompt = f"""{base_context}

COUNCIL DISCUSSION:
{other_thoughts}

BRIEFLY respond from YOUR perspective (1-2 sentences). {debate_angles[i]} What's your key point?"""
        
        try:
            response = grok_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": member['persona'] + " You have a DIFFERENT perspective than your colleagues. Challenge their views from YOUR angle. Be very brief. Maximum 2 sentences."},
                    {"role": "user", "content": debate_prompt}
                ],
                temperature=0.9,  # Higher temperature for diverse responses
                max_tokens=100
            )
            
            debate_response = response.choices[0].message.content
            debate_responses.append({
                "member": member["name"],
                "role": member["role"],
                "response": debate_response
            })
            
            if debate_container:
                with debate_container.expander(f"💬 {member['name']} responds"):
                    st.write(debate_response)
        except Exception as e:
            error_msg = str(e)
            if debate_container:
                st.error(f"Error from {member['name']}: {error_msg}")
            debate_responses.append({
                "member": member["name"],
                "role": member["role"],
                "response": f"Error: {error_msg}"
            })
    
    # STEP 3: Final votes after debate
    if debate_container:
        debate_container.subheader("🗳️ Final Voting")
        debate_container.write("Council members are now casting their final votes after the debate...")
    
    votes = []
    reasons = []
    
    for i, member in enumerate(COUNCIL_MEMBERS):
        # Compile full debate context
        all_thoughts = "\n\n".join([
            f"{t['member']}: {t['thought']}"
            for t in initial_thoughts
        ])
        all_responses = "\n\n".join([
            f"{r['member']}: {r['response']}"
            for r in debate_responses
        ])
        
        # Different voting focus for each member
        vote_focus = [
            "Base your vote on FINANCIAL RISK and NUMBERS. What do the metrics tell you?",
            "Base your vote on POTENTIAL and OPPORTUNITY. What growth do you see?",
            "Base your vote on EQUITY and CONTEXT. What circumstances matter most?"
        ]
        
        vote_prompt = f"""{base_context}

COUNCIL DISCUSSION:
{all_thoughts}

{all_responses}

{vote_focus[i]}

Cast your vote: APPROVE or REJECT
If REJECT, state the MAIN reason from YOUR perspective in 1 sentence.
If APPROVE, state why from YOUR perspective in 1 sentence.
Format: "VOTE: [APPROVE/REJECT] - [one sentence reason from your unique angle]"
"""
        
        try:
            response = grok_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": member['persona'] + " Vote based on YOUR unique perspective, not what others said. Think independently. Be extremely brief. One sentence only."},
                    {"role": "user", "content": vote_prompt}
                ],
                temperature=0.8,  # Slightly higher for more independent thinking
                max_tokens=80
            )
            
            vote_text = response.choices[0].message.content
            vote = "APPROVE" if "APPROVE" in vote_text.upper() else "REJECT"
            votes.append(vote)
            reasons.append({
                "member": member["name"],
                "role": member["role"],
                "vote": vote,
                "reason": vote_text,
                "initial_thought": initial_thoughts[i]["thought"],
                "debate_response": debate_responses[i]["response"] if i < len(debate_responses) else ""
            })
            
            if debate_container:
                vote_emoji = "✅" if vote == "APPROVE" else "❌"
                debate_container.write(f"{vote_emoji} **{member['name']}** votes: **{vote}**")
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "unauthorized" in error_msg.lower() or "invalid" in error_msg.lower() or "expired" in error_msg.lower():
                st.error(f"❌ API Key Error from {member['name']}: {error_msg}")
                st.error("Please check your GROK_API_KEY. It may be invalid or expired.")
            else:
                st.error(f"Error getting vote from {member['name']}: {error_msg}")
            votes.append("REJECT")
            reasons.append({
                "member": member["name"],
                "role": member["role"],
                "vote": "REJECT",
                "reason": f"Error: {str(e)}",
                "initial_thought": initial_thoughts[i]["thought"] if i < len(initial_thoughts) else "",
                "debate_response": ""
            })
    
    # Count votes
    approve_count = votes.count("APPROVE")
    reject_count = votes.count("REJECT")
    final_decision = "APPROVE" if approve_count > reject_count else "REJECT"
    
    return {
        "decision": final_decision,
        "approve_votes": approve_count,
        "reject_votes": reject_count,
        "council_reasons": reasons
    }

def load_csv_data(filepath: str, max_rows: int = 1000):
    """Load CSV and return first max_rows as records."""
    df = pd.read_csv(filepath, nrows=max_rows)
    records = []
    for idx, row in df.iterrows():
        records.append({
            "text": str(row.to_dict()),
            "id": f"row_{idx}"
        })
    return records

# Streamlit UI
st.set_page_config(page_title="Loan Application Processor", layout="wide")
st.title("🏦 Loan Application Processing System")
st.markdown("---")

# Sidebar for data loading
with st.sidebar:
    st.header("📊 Data Management")
    
    if st.button("Load CSV Data (First 1000 rows)", type="primary"):
        with st.spinner("Loading CSV and storing in Qdrant..."):
            try:
                records = load_csv_data('loan_data.csv', max_rows=1000)
                count = store_loan_applications_batch(records)
                st.success(f"✅ Loaded and stored {count} loan applications!")
                
                # Show collection status
                collection_count = qdrant_client.count(collection_name="loan_applications")
                st.info(f"📈 Total records in collection: {collection_count.count}")
            except Exception as e:
                st.error(f"Error loading data: {e}")
    
    st.markdown("---")
    st.header("🔍 Search & Process")
    
    # Check collection status
    try:
        collection_count = qdrant_client.count(collection_name="loan_applications")
        st.metric("Records in Collection", collection_count.count)
    except:
        st.warning("Collection not initialized. Load data first.")

# Main area
tab1, tab2 = st.tabs(["📝 Process Application", "📊 View Collection"])

with tab1:
    st.header("Process New Loan Application")
    
    # Text input for application
    application_text = st.text_area(
        "Enter loan application details:",
        height=200,
        placeholder="Example: Applicant: John Doe, Age: 35, Income: $75,000/year, Credit Score: 720, Loan Amount: $50,000, Purpose: Home renovation, Employment: Software Engineer, 5 years..."
    )
    
    if st.button("🚀 Process Application", type="primary"):
        if not application_text.strip():
            st.warning("Please enter an application first!")
        else:
            # Check if collection has data
            try:
                collection_count = qdrant_client.count(collection_name="loan_applications")
                if collection_count.count == 0:
                    st.warning("⚠️ No data loaded! Please load CSV data from the sidebar first.")
                    st.stop()
            except:
                st.warning("⚠️ Collection not initialized! Please load CSV data from the sidebar first.")
                st.stop()
            
            with st.spinner("Processing application..."):
                # Step 1: Similarity search
                st.subheader("Step 1: Finding Similar Applications")
                similar_apps = similarity_search(application_text, top_k=5)
                
                if similar_apps:
                    st.success(f"Found {len(similar_apps)} similar applications")
                    with st.expander("View Similar Applications"):
                        for i, app in enumerate(similar_apps, 1):
                            st.markdown(f"**Similar App {i}** (Score: {app['score']:.3f})")
                            st.text(app['text'][:300] + "...")
                            st.divider()
                else:
                    st.info("No similar applications found.")
                
                # Step 2: LLM Council Debate & Vote
                st.subheader("Step 2: LLM Council Debate & Voting")
                
                # Create container for debate
                debate_container = st.container()
                vote_result = llm_council_vote(application_text, similar_apps, debate_container=debate_container)
                
                # Display results
                st.markdown("---")
                st.header("🎯 Council Decision")
                
                # Decision badge
                if vote_result['decision'] == "APPROVE":
                    st.success(f"✅ **FINAL DECISION: APPROVE** ({vote_result['approve_votes']}/3 votes)")
                else:
                    st.error(f"❌ **FINAL DECISION: REJECT** ({vote_result['reject_votes']}/3 votes)")
                
                # Council member votes - brief display
                st.subheader("Council Member Final Votes")
                for reason in vote_result['council_reasons']:
                    vote_emoji = "✅" if reason['vote'] == 'APPROVE' else "❌"
                    vote_color = "green" if reason['vote'] == 'APPROVE' else "red"
                    
                    # Extract main reason from vote text
                    vote_reason = reason.get('reason', '')
                    if reason['vote'] == 'REJECT':
                        # For rejections, highlight the main reason
                        st.markdown(f"### {vote_emoji} **{reason['member']}** ({reason['role']}) - **{reason['vote']}**")
                        st.markdown(f"**Main Reason:** {vote_reason}")
                    else:
                        st.markdown(f"### {vote_emoji} **{reason['member']}** ({reason['role']}) - **{reason['vote']}**")
                        st.markdown(f"**Reason:** {vote_reason}")
                    st.divider()

with tab2:
    st.header("Collection Overview")
    
    try:
        collection_count = qdrant_client.count(collection_name="loan_applications")
        st.metric("Total Records", collection_count.count)
        
        if collection_count.count > 0:
            # Get sample records
            records = qdrant_client.scroll(
                collection_name="loan_applications",
                limit=10
            )[0]
            
            st.subheader("Sample Records")
            for i, record in enumerate(records, 1):
                with st.expander(f"Record {i} - ID: {record.id}"):
                    text = record.payload.get('text', 'N/A')
                    st.text(text[:500] + "..." if len(text) > 500 else text)
        else:
            st.info("Collection is empty. Load data from the sidebar.")
    except Exception as e:
        st.error(f"Error accessing collection: {e}")
        st.info("Load data from the sidebar first.")
