# ============================================================
# PART 1 — IMPORTS AND ENVIRONMENT
# ============================================================


import os

from dotenv import load_dotenv
from qdrant_client import  QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from groq import Groq

# Load variables from .env

load_dotenv()
QDRANT_URL=os.getenv("QDRANT_URL")
QDRANT_API_KEY=os.getenv("QDRANT_API_KEY")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")



# ============================================================
# PART 2 — CONNECT TO QDRANT
# ============================================================

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

print("Connected to Qdrant Cloud.\n")



# ============================================================
# STEP-3 : CREATE QDRANT COLLECTION--> which have 3 sections::->
    # i) id(unique Qdrant_id)
    # ii) vector
    # iii) payload
# ============================================================

COLLECTION_NAME= "knowledge"
EMBEDDING_SIZE= 384


# Delete the collection if it already exists
if client.collection_exists(COLLECTION_NAME):
    print(f"Deleting the existing collection:{COLLECTION_NAME}")
    client.delete_collection(COLLECTION_NAME)
    print(f"Deleted the existing collection:{COLLECTION_NAME}")


# Create Collection

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=EMBEDDING_SIZE,
        distance=Distance.COSINE,
    ),
)

print(f"Created Collection: {COLLECTION_NAME}")
print(f"Vector size: {EMBEDDING_SIZE}")
print("Distance: COSINE")





# =====================================================
# STEP - 4 :LOAD OUR KNOWLEDGE
# =====================================================

with open("knowledge.txt", "r", encoding="utf-8") as f:
    documents = [
        line.strip()
        for line in f
        if line.strip()
    ]

#["line 1 ","line 2 ", "line 3", ....]
print(f"Loaded {len(documents)} documents")



# ==================================================
# STEP - 5: CREATE EMBEDDINGS
# ==================================================

print("Loading embedding model....")
model=SentenceTransformer("all-MiniLM-L6-v2") # it will create 384 features

print("Embedding Model is Ready Now!!")


embeddings = model.encode(documents)

print(f"Generated {len(embeddings)} embeddings")
print(f"Embedding size: {len(embeddings[0])}")



# ==================================================
# STEP - 6: CREATE QDRANT POINTS
# ==================================================

points = []
for i,embedding in enumerate(embeddings):

    point = PointStruct(
        # i) id
        id = i + 1, #id=1
        
        # ii) vector
        vector = embedding.tolist(),

        # iii) payload
        payload={
            "text":documents[i]
        }
    )

    points.append(point)



# ==================================================
# STEP -7: UPLOAD TO QDRANT
# ==================================================

# upsert :==> upload + insert  (if duplications is there update the content)
client.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)


print(f"Uploaded {len(points)} documents to Qdrant!")

# ============================================================
# STEP 8 — SEARCH QDRANT
# ============================================================

def search(query, top_k=3):

    # Convert the question into an embedding
    query_vector= model.encode(query).tolist()

    # Search Qdrant for similar vectors 
    results =client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points
    
    return results

# ============================================================
# STEP 9 — TEST SEARCH
# ============================================================

query= "How many vacation days do I get ? "

results = search(query, top_k=3)


print("\n Search results:")

print("#####################################")
print(f"results:\n", results)


for result in results:
    print(f"Score: {result.score:.3f}")
    print(result.payload["text"])
    print()


# ===================================================================
# STEP -10: CONNECT TO GROQ
# ===================================================================


groq_client = Groq(
    api_key=GROQ_API_KEY
)


# ====================================================================
#   STEP - 11: ASK THE LLM
# ===================================================================

def ask_llm(question, context):
    prompt=  f"""
Answer the question using only the information provided below.

Context:
{context}

Question:
{question}


If the answer is not present in the context, say:
"I don't know based on the provided information."
"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role" : "user",
                "content":prompt
            }
        ]
    )

    return response.choices[0].message.content





# ==========================================================================
# STEP - 12: COMPLETE RAG PIPELINE
# ==========================================================================


question = "How many vacation days do I get ? "

results=search(question, top_k=3)



# Extract text from the search results
context = "\n".join(
    result.payload["text"]
    for result in results
)


answer = ask_llm(question, context)

print("\n Final Answer: ")
print(answer)