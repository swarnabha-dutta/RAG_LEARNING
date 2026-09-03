# ===============================================
# STEP - 1: IMPORTS AND ENVIRONMENT
# ===============================================


import os


from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, FieldCondition, MatchValue, MatchAny, PayloadSchemaType
from sentence_transformers import SentenceTransformer
# from groq import Groq

import json



# load variables from .env

load_dotenv()


QDRANT_URL=os.getenv("QDRANT_URL")
QDRANT_API_KEY=os.getenv("QDRANT_API_KEY")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")



# ===============================================
# STEP - 2: CONNECT TO QDRANT
# ===============================================


client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)


print("Connected to Qdrant Client")

# ===============================================
# STEP - 3: CREATE QDRANT COLLECTION
# ===============================================


COLLECTION_NAME="knowledge filter"
EMBEDDING_SIZE=384

# Delete collection if it already exists
if client.collection_exists(COLLECTION_NAME):
    print(f"Deleting existing collection:{COLLECTION_NAME}")
    client.delete_collection(COLLECTION_NAME)


# create collection

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=EMBEDDING_SIZE,
        distance=Distance.COSINE
    ),
)


print(f"Created collection: {COLLECTION_NAME}")
print(f"Vector size:{EMBEDDING_SIZE}")
print("Distance: COSINE")

client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="category",
    field_schema=PayloadSchemaType.KEYWORD
)




# ============================================================
# STEP -4 : LOAD OUR KNOWLEDGE
# ============================================================



with open("knowledge.json", "r", encoding="utf-8") as f:
    documents = json.load(f)# i actually read the JSON files to python object
    # like:
#     documents = [
#     {
#         "text": "Employees receive 24 days of paid leave per year.",
#         "category": "leave",
#         "is_active": True
#     },

#     {
#         "text": "Employees work from the office on Tuesday, Wednesday and Thursday.",
#         "category": "workplace",
#         "is_active": True
#     },

#     {
#         "text": "Employees receive Rs 3000 per month for gym reimbursement.",
#         "category": "reimbursement",
#         "is_active": True
#     }
# ]

# ============================================================
# STEP - 5 : CREATE EMBEDDINGS
# ============================================================

print("Loading embedding model...")


model= SentenceTransformer("all-MiniLM-L6-v2") #384

print("Embedding model ready!")

texts = [document["text"] for document in documents]

embeddings = model.encode(texts)


print(f"Generated {len(embeddings)} embeddings")