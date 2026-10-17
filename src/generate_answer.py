from speech_to_text import transcribe_voice_question
import os
from dotenv import load_dotenv

from groq import Groq

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


# Load API key from .env
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")


# Create Groq client
client = Groq(api_key=api_key)


# ChromaDB location
CHROMA_DB_DIR = "chroma_db"


# Same embedding model used while creating ChromaDB
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Connect to existing ChromaDB
vector_db = Chroma(
    persist_directory=CHROMA_DB_DIR,
    embedding_function=embedding_model
)


# Ask the user
query = transcribe_voice_question()


# Retrieve relevant agriculture information
retrieved_docs = vector_db.similarity_search(query, k=5)


# Combine retrieved documents
context = ""

for idx, doc in enumerate(retrieved_docs, start=1):
    context += f"\n--- Source {idx} ---\n"
    context += doc.page_content


# Send retrieved information to LLM
prompt = f"""
You are an agricultural advisory assistant.

Answer the farmer's question ONLY using the information
provided in the context below.

Do not add information from your own knowledge.

If the context does not contain enough information to answer
the question, say:

"Insufficient information in the agricultural knowledge base."

Context:
{context}

Farmer's Question:
{query}

Answer:
"""


response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": "You are a careful agricultural information assistant."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0
)


answer = response.choices[0].message.content
answer = "The season for cotton cultivation is Rabi."


print("\n--- GENERATED ANSWER ---")
print(answer)
# ---------------- ANSWER VERIFICATION ----------------

verification_prompt = f"""
You are an answer verification system.

Your task is to check whether the generated answer is supported
by the retrieved agricultural context.

Rules:
1. Use ONLY the provided context as evidence.
2. If all important information in the answer is supported, return SUPPORTED.
3. If some information is supported but some is not, return PARTIALLY SUPPORTED.
4. If the answer is not supported by the context, return UNSUPPORTED.
5. Do not use your own knowledge.
6. Give a short reason.

Retrieved Context:
{context}

Generated Answer:
{answer}

Return the result in this format:

Status: SUPPORTED / PARTIALLY SUPPORTED / UNSUPPORTED
Reason: <short explanation>
"""


verification_response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": "You are a careful answer verification system."
        },
        {
            "role": "user",
            "content": verification_prompt
        }
    ],
    temperature=0
)

verification = verification_response.choices[0].message.content


print("\n--- ANSWER VERIFICATION ---")
print(verification)