import pandas as pd
import os
from typing import Optional

# Import functions from loan_processor to store data into Qdrant
from loan_processor import store_loan_application, setup_qdrant_collection, store_loan_applications_batch, show_collection_status


def upsert_text(application_text: str, application_id: str):
    """Helper to ensure collection exists and upsert the provided text as an application."""
    setup_qdrant_collection()
    store_loan_application(application_text, application_id)


if __name__ == "__main__":
    # Load CSV
    df = pd.read_csv('loan_data.csv')
    
    # Prepare all records at once
    records = []
    for idx, row in df.iterrows():
        records.append({
            "text": str(row.to_dict()),
            "id": f"row_{idx}"
        })
        if idx==3000:
            break
    
    # Insert ALL at once
    print("Setting up collection...")
    setup_qdrant_collection()
    print(f"Storing {len(records)} records...")
    store_loan_applications_batch(records)
    print(f"Inserted {len(records)} records in one batch")
    
    # Show collection status
    print("\n" + "="*60)
    print("COLLECTION STATUS:")
    show_collection_status()
    print("="*60)
    

