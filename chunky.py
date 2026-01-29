import uuid
from chonkie import Chunkie
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

# 1. Setup Models and Database
# Initialize the embedding model (converts text to numbers)
encoder = SentenceTransformer('all-MiniLM-L6-v2') 

# Initialize Qdrant in-memory for testing purposes
client = QdrantClient(":memory:") 

# Create a collection to store the credit decision vectors
client.recreate_collection(
    collection_name="credit_decisions_chonkie",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# 2. Define the Loan Application Data
# This represents the full "Parent Document" containing mixed information
loan_app = """
Applicant ID: 5042. Name: Sami Ben Foulen. 
Employment status is stable, working as a Software Engineer for 5 years. 
Income is verified at 4,500 TND monthly. 
However, behavioral analysis detected high-risk activity. 
On Jan 15th, user transferred 80% of salary to a known online gambling platform.
Credit utilization is currently at 30%.
"""

# 3. Initialize the Chunker
# We use a small chunk_size (e.g., 50 tokens) to demonstrate splitting on this short text.
# In production, you might use 200 or 500 depending on the model context window.
chunker = Chunkie(chunk_size=50) 

# Perform the chunking operation
chunks = chunker.chunk(loan_app)

print(f"Processing {len(chunks)} chunks from the document...\n")

# 4. Vectorization and Indexing Loop
points = []

for i, chunk in enumerate(chunks):
    # 'chunk' is an object containing text and metadata (like token count)
    text_content = chunk.text
    
    # Generate the vector embedding for this specific chunk
    vector = encoder.encode(text_content).tolist()
    
    # Prepare the payload (Metadata)
    # KEY STRATEGY: We store the chunk text AND the full parent context
    payload = {
        "chunk_id": i,
        "chunk_text": text_content,
        "token_count": chunk.token_count,
        "parent_context": loan_app,  # Storing the full doc for retrieval context
        "risk_flag": "gambling" if "gambling" in text_content else "neutral"
    }
    
    # Create the Point structure for Qdrant
    points.append(
        PointStruct(
            id=str(uuid.uuid4()), 
            vector=vector, 
            payload=payload
        )
    )
    
    print(f"Example Chunk [{i}]: {text_content} (Tokens: {chunk.token_count})")

# 5. Upload to Qdrant
client.upsert(collection_name="credit_decisions_chonkie", points=points)

print("\nSuccess: All chunks have been indexed in Qdrant.")