# hackathon-qdrant
llm council that decides loan approval (just a grok api with different personas for now)

Architecture:

load data vias csv_read

embed directly using fastembed

user inputs his loan applicatio

perform similarity search

an llm council decides wether to approve loan 
done by voting
