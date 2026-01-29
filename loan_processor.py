"""
Simple Loan Application Processing System
Takes a loan application, chunks it, embeds it, does similarity search,
and uses an LLM council to vote on approval.
"""

import os
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from fastembed import TextEmbedding
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize clients
qdrant_client = QdrantClient(":memory:")  # In-memory for simplicity
embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Simple text chunking function.
    Splits text into overlapping chunks.
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - chunk_overlap
    
    return chunks


def embed_chunks(chunks: List[str]) -> List[List[float]]:
    """
    Embed chunks using FastEmbed from Qdrant.
    """
    embeddings = list(embedding_model.embed(chunks))
    return [embed.tolist() for embed in embeddings]


def setup_qdrant_collection(collection_name: str = "loan_applications"):
    """
    Set up Qdrant collection for storing loan applications.
    """
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


def store_loan_application(application_text: str, application_id: str, collection_name: str = "loan_applications"):
    """
    Store a loan application by chunking, embedding, and storing in Qdrant.
    """
    # Chunk the application
    chunks = chunk_text(application_text)
    
    # Embed chunks
    embeddings = embed_chunks(chunks)
    
    # Store in Qdrant
    points = [
        PointStruct(
            id=hash(f"{application_id}_{i}") % (2**63),  # Simple hash for ID
            vector=embedding,
            payload={"chunk_text": chunk, "application_id": application_id, "chunk_index": i}
        )
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    
    qdrant_client.upsert(collection_name=collection_name, points=points)
    print(f"Stored loan application {application_id} with {len(chunks)} chunks")


def similarity_search(query_text: str, top_k: int = 5, collection_name: str = "loan_applications") -> List[Dict]:
    """
    Perform similarity search to find similar loan applications.
    """
    # Embed the query
    query_embedding = list(embedding_model.embed([query_text]))[0].tolist()
    
    # Search in Qdrant
    results = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        limit=top_k
    )
    
    return [
        {
            "score": result.score,
            "chunk_text": result.payload["chunk_text"],
            "application_id": result.payload.get("application_id", "unknown")
        }
        for result in results
    ]


def llm_council_vote(application_text: str, similar_applications: List[Dict]) -> Dict:
    """
    LLM council votes on whether to accept the loan application.
    """
    # Prepare context from similar applications
    if similar_applications:
        similar_context = "\n".join([
            f"Similar application (score: {app['score']:.3f}): {app['chunk_text'][:200]}..."
            for app in similar_applications[:3]
        ])
    else:
        similar_context = "No similar applications found in database."
    
    # Create prompt for council
    prompt = f"""You are part of an AI loan approval council. Review the loan application and similar past applications to make a decision.

NEW LOAN APPLICATION:
{application_text}

SIMILAR PAST APPLICATIONS:
{similar_context}

Based on the application and similar cases, vote:
- APPROVE: If the loan should be approved
- REJECT: If the loan should be rejected

Provide your vote and a brief reason (1-2 sentences)."""

    # Get votes from multiple "council members" (multiple calls)
    votes = []
    reasons = []
    
    for i in range(3):  # 3 council members
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a loan approval expert. Be concise."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        vote_text = response.choices[0].message.content
        votes.append("APPROVE" if "APPROVE" in vote_text.upper() else "REJECT")
        reasons.append(vote_text)
    
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


def process_loan_application(application_text: str, application_id: str):
    """
    Main function to process a loan application.
    """
    print(f"\n{'='*60}")
    print(f"Processing Loan Application: {application_id}")
    print(f"{'='*60}\n")
    
    # Step 1: Store the application (chunk, embed, store)
    print("Step 1: Chunking and storing application...")
    store_loan_application(application_text, application_id)
    
    # Step 2: Similarity search
    print("\nStep 2: Performing similarity search...")
    similar_apps = similarity_search(application_text, top_k=5)
    print(f"Found {len(similar_apps)} similar applications:")
    for i, app in enumerate(similar_apps, 1):
        print(f"  {i}. Score: {app['score']:.3f} - {app['chunk_text'][:100]}...")
    
    # Step 3: LLM Council Vote
    print("\nStep 3: LLM Council voting...")
    vote_result = llm_council_vote(application_text, similar_apps)
    
    # Step 4: Display results
    print(f"\n{'='*60}")
    print("COUNCIL DECISION:")
    print(f"{'='*60}")
    print(f"Final Decision: {vote_result['decision']}")
    print(f"Approve Votes: {vote_result['approve_votes']}/3")
    print(f"Reject Votes: {vote_result['reject_votes']}/3")
    print(f"\nCouncil Reasons:")
    for i, reason in enumerate(vote_result['council_reasons'], 1):
        print(f"  Member {i}: {reason[:150]}...")
    print(f"{'='*60}\n")
    
    return vote_result


if __name__ == "__main__":
    # Setup Qdrant collection
    setup_qdrant_collection()
    
    # Example: Store some reference loan applications first
    print("Storing reference loan applications...")
    reference_apps = [
        ("REF001", "Loan application for $50,000. Applicant: John Doe, Age: 35, Income: $80,000/year, Credit Score: 750, Employment: Software Engineer, 5 years at current job. Purpose: Home renovation. Collateral: None."),
        ("REF002", "Loan application for $25,000. Applicant: Jane Smith, Age: 28, Income: $60,000/year, Credit Score: 680, Employment: Teacher, 3 years at current job. Purpose: Car purchase. Collateral: Car (value: $30,000)."),
        ("REF003", "Loan application for $100,000. Applicant: Bob Johnson, Age: 45, Income: $120,000/year, Credit Score: 720, Employment: Manager, 10 years at current job. Purpose: Business expansion. Collateral: Property (value: $150,000)."),
    ]
    
    for app_id, app_text in reference_apps:
        store_loan_application(app_text, app_id)
    
    # Process a new loan application
    new_application = """
    Loan application for $75,000.
    Applicant: Alice Williams, Age: 32
    Income: $95,000/year
    Credit Score: 710
    Employment: Marketing Director, 4 years at current job
    Purpose: Business startup
    Collateral: Savings account ($40,000)
    """
    
    result = process_loan_application(new_application, "NEW001")
