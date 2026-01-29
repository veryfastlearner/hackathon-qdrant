from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
import uuid
from typing import List, Dict, Any
import json


class QdrantLoanDatabase:
    """
    Qdrant-based historical loan database for credit decision support
    """
    
    def __init__(self, persist_directory: str = "./qdrant_loan_data"):
        print("🏦 Initializing Qdrant Loan Database...")
        
        # Initialize Qdrant client
        self.qdrant = QdrantClient(path=persist_directory)
        print("✅ Qdrant client connected")
        
        # Initialize embedding model
        print("📥 Loading embedding model...")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model loaded")
        
        self.collection_name = "loan_cases"
        
        # Create collection if it doesn't exist
        self._initialize_collection()
        
    def _initialize_collection(self):
        """Create the loan cases collection"""
        try:
            self.qdrant.get_collection(self.collection_name)
            print(f"✅ Using existing collection '{self.collection_name}'")
        except:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384,  # all-MiniLM-L6-v2 dimension
                    distance=Distance.COSINE
                )
            )
            print(f"✅ Created new collection '{self.collection_name}'")
            
    def add_historical_cases(self, cases: List[Dict[str, Any]]):
        """
        Add historical loan cases to Qdrant
        
        Each case should have:
        - id: unique identifier (will be stored in payload, not as Qdrant ID)
        - applicant_profile: text description
        - loan_amount: float
        - status: 'Repaid' or 'Defaulted'
        - grade: loan grade (A-E)
        - dti: debt-to-income ratio
        - credit_score: int
        - employment_status: str
        - repayment_behavior: str
        - key_risk_factors: list of strings
        - category: str (filtering category)
        - region: str (geographic region)
        """
        print(f"\n📝 Adding {len(cases)} historical cases to Qdrant...")
        points = []
        
        for i, case in enumerate(cases, 1):
            case_id = case.get('id', f'CASE-{i}')
            print(f"  Processing case {i}/{len(cases)}: {case_id}")
            
            # Create text representation for embedding
            text_repr = self._create_text_representation(case)
            
            # Generate embedding
            vector = self.encoder.encode(text_repr).tolist()
            
            # IMPORTANT: Always generate a new UUID for Qdrant
            # Store the original ID in the payload
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),  # Generate proper UUID
                    vector=vector,
                    payload={
                        "original_id": case_id,  # Store original ID here
                        "applicant_profile": case.get('applicant_profile', ''),
                        "loan_amount": case.get('loan_amount', 0),
                        "status": case.get('status', 'Unknown'),
                        "grade": case.get('grade', 'C'),
                        "dti": case.get('dti', 0),
                        "credit_score": case.get('credit_score', 600),
                        "employment_status": case.get('employment_status', 'employed'),
                        "repayment_behavior": case.get('repayment_behavior', ''),
                        "key_risk_factors": case.get('key_risk_factors', []),
                        "category": case.get('category', 'Standard Retail'),
                        "region": case.get('region', 'Global')
                    }
                )
            )
        
        # Upsert to Qdrant
        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"✅ Successfully added {len(cases)} historical cases!\n")
    
    def _create_text_representation(self, case: Dict[str, Any]) -> str:
        """Create a rich text representation of a loan case for embedding"""
        parts = [
            f"Applicant Profile: {case.get('applicant_profile', '')}",
            f"Loan Amount: ${case.get('loan_amount', 0):,.2f}",
            f"Credit Grade: {case.get('grade', 'Unknown')}",
            f"DTI Ratio: {case.get('dti', 0):.1f}%",
            f"Credit Score: {case.get('credit_score', 'Unknown')}",
            f"Employment: {case.get('employment_status', 'Unknown')}",
            f"Status: {case.get('status', 'Unknown')}",
            f"Repayment Behavior: {case.get('repayment_behavior', '')}",
            f"Risk Factors: {', '.join(case.get('key_risk_factors', []))}",
            f"Category: {case.get('category', '')}",
            f"Region: {case.get('region', '')}"
        ]
        return " | ".join(parts)
    
    def search_similar_cases(
        self, 
        application: Dict[str, Any], 
        limit: int = 9,
        category_filter: str = None,
        region_filter: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar historical cases using vector similarity
        
        Args:
            application: Current loan application data
            limit: Number of similar cases to return
            category_filter: Filter by loan category
            region_filter: Filter by geographic region
            
        Returns:
            List of similar cases with similarity scores
        """
        print(f"\n🔍 Searching for {limit} similar historical cases...")
        
        # Create query text from application
        query_text = self._create_query_text(application)
        print(f"📝 Query: {query_text[:100]}...")
        
        # Generate query vector
        query_vector = self.encoder.encode(query_text).tolist()
        
        # Build filter if needed
        search_filter = None
        if category_filter or region_filter:
            conditions = []
            if category_filter:
                conditions.append(
                    FieldCondition(
                        key="category",
                        match=MatchValue(value=category_filter)
                    )
                )
            if region_filter:
                conditions.append(
                    FieldCondition(
                        key="region",
                        match=MatchValue(value=region_filter)
                    )
                )
            if conditions:
                search_filter = Filter(must=conditions)
        
        # Search Qdrant
        results = self.qdrant.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            query_filter=search_filter
        ).points
        
        print(f"✅ Found {len(results)} similar cases")
        
        # Format results - use original_id from payload
        similar_cases = []
        for hit in results:
            similar_cases.append({
                "id": hit.payload.get("original_id", str(hit.id)),  # Use original_id
                "similarity": hit.score,
                "status": hit.payload.get("status"),
                "loan_amount": hit.payload.get("loan_amount"),
                "applicant_profile": hit.payload.get("applicant_profile"),
                "grade": hit.payload.get("grade"),
                "dti": hit.payload.get("dti"),
                "credit_score": hit.payload.get("credit_score"),
                "repayment_behavior": hit.payload.get("repayment_behavior"),
                "key_risk_factors": hit.payload.get("key_risk_factors", []),
                "category": hit.payload.get("category"),
                "region": hit.payload.get("region")
            })
        
        return similar_cases
    
    def _create_query_text(self, application: Dict[str, Any]) -> str:
        """Create query text from loan application"""
        dti = 0
        if application.get('monthly_income', 0) > 0:
            dti = (application.get('existing_debt', 0) / application['monthly_income']) * 100
            
        parts = [
            f"Loan Amount: ${application.get('amount', 0):,.2f}",
            f"Purpose: {application.get('purpose', '')}",
            f"Monthly Income: ${application.get('monthly_income', 0):,.2f}",
            f"DTI Ratio: {dti:.1f}%",
            f"Credit Score: {application.get('credit_score', 0)}",
            f"Employment: {application.get('employment_status', '')}",
            f"Employment Years: {application.get('employment_years', 0)}",
            f"Location: {application.get('business_location', 'Unknown')}"
        ]
        return " | ".join(parts)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the loan database"""
        try:
            collection_info = self.qdrant.get_collection(self.collection_name)
            return {
                "total_cases": collection_info.points_count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance
            }
        except Exception as e:
            return {"error": str(e)}
