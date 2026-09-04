# ==========================================
#  STEP - 1 : IMPORTS AND ENVIRONMENT
# ==========================================


import os

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, MatchAny, PayloadSchemaType
from sentence_transformers import SentenceTransformer

from groq import Groq
import json

# load secret variables form .env
load_dotenv()

QDRANT_URL=os.getenv("QDRANT_URL")
QDRANT_API_KEY=os.getenv("QDRANT_API_KEY")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")



# ==========================================
#  STEP - 2 : CONNECT TO QDRANT
# ==========================================

qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)


# ==========================================
#  STEP - 3 : CREATE QDRANT COLLECTION
# ==========================================

COLLECTION_NAME="knowledge_filter"
EMBEDDING_SIZE = 384

# Delete collection if it already exists
if qdrant_client.collection_exists(COLLECTION_NAME):
    print(f"Deleting existing collection: {COLLECTION_NAME}")
    qdrant_client.delete_collection(COLLECTION_NAME)


# Create Collection

# Basically in pydantic in Collection each information have points and each point have an id(unique) , vector and payload
qdrant_client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams( 
        size=EMBEDDING_SIZE,
        distance=Distance.COSINE,
    ),
)

print(f"Created collection: {COLLECTION_NAME}")
print(f"Vector size: {EMBEDDING_SIZE}")
print("DISTANCE: COSINE")

qdrant_client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="category",
    field_schema=PayloadSchemaType.KEYWORD
)
print("qdrant_client:",qdrant_client)

# ==========================================
#  STEP - 4 : LOAD OUR KNOWLEDGE
# ==========================================

# it read the data and convert the file from json to python object or python list
with open("knowledge.json", "r", encoding="utf-8") as f:
    documents = json.load(f)


# # ==========================================
# #  STEP - 5 : CREATE EMBEDDINGS
# # ==========================================

print("Loading Embedding Model...")


model= SentenceTransformer("all-MiniLM-L6-v2")# it has 384 vector features

print(f"Embedding Model Ready!")

texts=[document["text"] for document in documents]


# documents = [
#     {"text": "You get 20 vacation days.", "category": "leave"},
#     {"text": "Medical reimbursement is available.", "category": "reimbursement"}
# ]

# texts=[
#     "You get 20 vacation days.",
#     "Medical reimbursement is available."
# ]



# Convert documents python list(Array of objects) to separate the keys name text to array of strings 
# print(f"texts is:\n ", texts)



embeddings = model.encode(texts)

# Generated 100 embeddings
# Embedding 1:  "You get 20 vacation days."
# Embedding 2:  "Medical reimbursement is available."
# :
# :
# Embedding n:"..."

print(f"Generated {len(embeddings)} embeddings")
print(f"Embedding size:{len(embeddings[0])}")

# ============================================================
# STEP - 6 : CREATE QDRANT POINTS
# ============================================================

points = []

for i in range(len(documents)):

    point = PointStruct(
        id = i + 1,
        vector = embeddings[i].tolist(),
        payload=documents[i]
    )

    points.append(point)

    # print("points: \n",points)


# ============================================================
# STEP - 7 : UPLOAD TO QDRANT
# ============================================================

# UPSERT==> UPLOAD + INSERT --> if new data then insert and upload else do nothing


qdrant_client.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)


print(f"Uploaded {len(points)} documents to Qdrant!")

# ============================================================
# STEP - 8 : SEARCH QDRANT
# ============================================================



def search(query, top_k=3):
    # Convert the question into an embedding
    query_vector = model.encode(query).tolist()

    # Search Qdrant for similar vectors
    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points

    return results
    

def search_with_filter(query, query_filter=None, top_k=3):


    query_vector = model.encode(query).tolist()

    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
        query_filter=query_filter
    ).points

    return results

reimbursement_filter = Filter(
    must=[
        FieldCondition(
            key="category",
            match=MatchValue(value="reimbursement")
        )
    ]
)
leave_filter = Filter(
    must=[
        FieldCondition(
            key="category",
            match=MatchValue(value="leave")
        )
    ]
)

workplace_filter = Filter(
    must =[
        FieldCondition(
            key="category",
            match=MatchValue(value="workplace")
        )
    ]
)




career_filter = Filter(
    must=[
        FieldCondition(
            key="category",
            match=MatchValue(value="career")
        )
    ]
)


attendance_filter = Filter(
    must = [
        FieldCondition(
            key="category",
            match=MatchValue(value="attendance")
        )
    ]
)

benefits_filter= Filter (
    must=[
        FieldCondition(
            key="category",
            match=MatchValue(value="benefits")
        )
    ]
)



training_filter = Filter(
    must=[
        FieldCondition(
            key="category",
            match=MatchValue(value="training")
        )
    ]
)




# ============================================================
# STEP - 9 : TEST SEARCH
# ============================================================

question = "How many sick leave days can I take?"

results = search_with_filter(
    question,
    leave_filter,
    top_k=3
)


print("\n Search Results: ")

for result in results:
    print(f"Score: {result.score:.3f}")
    print(result.payload["text"])
    print(result.payload["category"]) 
    print(result.payload["is_active"]) 
    print()


# ============================================================
#  STEP - 10: CONNECT TO GROQ
# ============================================================

groq_client= Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# STEP - 11 : ASK THE LLM
# ============================================================

def ask_llm(question, context):
    prompt= f"""
    Answer the question using only the information provided below.

    Context:
    {context}

    Question:
    {question}
    

    If the answer is not present in the context, say :
    "I don't know based on the provided information."
    """
    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role":"user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# ============================================================
# STEP - 12 : COMPLETE RAG PIPELINE
# ============================================================

question = "How many sick leave days can I take?"


results = search_with_filter(
    question,
    leave_filter,
    top_k=3
)

# Extract text from search results
context = "\n".join(
    result.payload["text"]
    for result in results
)


answer = ask_llm(question, context)

print("\n Final Answer: ")
print(answer)