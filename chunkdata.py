from chonkie import Chunkie
loan_app=""
chunker = Chunkie(chunk_size=200)

# Get chunks
chunks = chunker.chunk(loan_app)
