import pandas as pd
from qdrant_client import QdrantClient, models
from fastembed import TextEmbedding
import uuid
from qdrant_client.models import PointStruct

# Load CSV
df = pd.read_csv('C:/Users/Lenovo/Documents/Experiment/FinSight/data/main_jpm_transcripts.csv')

if 'Title' not in df.columns or 'Text' not in df.columns:
    raise ValueError("CSV must contain 'Title' and 'Text' columns")

# Initialize Qdrant client
client = QdrantClient("localhost", port=6333)

embedder = TextEmbedding()

# Combine 'Title' and 'Text' for better embeddings
documents = [f"{row['Title']} {row['Text']}" for _, row in df.iterrows()]
metadata = df.to_dict(orient="records")  # Store full row metadata
ids = [str(uuid.uuid4()) for _ in range(len(documents))]

# Convert text to embeddings
embeddings = list(embedder.embed(documents))
vector_size = len(embeddings[0])

# Create collection if not exists
collection_name = "JPM_Transcripts"

if client.collection_exists(collection_name):
    client.delete_collection(collection_name)

client.create_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
)

# Insert data into Qdrant
client.upload_points(
    collection_name=collection_name,
    points=[
        PointStruct(id=ids[i], vector=embeddings[i], payload=metadata[i])
        for i in range(len(documents))
    ],
)

# Example Query
query_text = "JPMorgan Chase Q4 2023 Earnings call full transcript"
query_embedding = list(embedder.embed([query_text]))[0]

search_result = client.query_points(
    collection_name=collection_name,
    query=query_embedding,
    limit=5
)

#print(search_result)

# Save search results to a text file
output_file = "search_results.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"Query: {query_text}\n\n")
    f.write(str(search_result))  # Directly convert to string

print(f"Search results saved to {output_file}")