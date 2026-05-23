import os
import requests
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3-8b-8192")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "chroma_db")


SYSTEM_PROMPT = """
You are PolicyAssist AI, a company policy assistant.

Rules:
1. Answer only using the provided policy context.
2. If the answer is not in the context, say:
   "I can only answer based on the company policy documents provided. I could not find that information in the policy corpus."
3. Always cite the source document title and file name.
4. Keep the answer clear and concise.
5. Do not invent policy details.
"""


def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings,
    )


def retrieve_context(question: str, k: int = 4):
    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search(question, k=k)
    return docs


def format_context(docs):
    context_parts = []

    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "Unknown source")
        title = doc.metadata.get("title", "Unknown title")
        content = doc.page_content

        context_parts.append(
            f"""
[Source {i}]
Title: {title}
File: {source}
Content:
{content}
"""
        )

    return "\n".join(context_parts)


def call_groq(prompt: str):
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY is not configured."

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 500,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]


def answer_question(question: str):
    docs = retrieve_context(question, k=4)
    context = format_context(docs)

    prompt = f"""
Use the following policy context to answer the user's question.

POLICY CONTEXT:
{context}

USER QUESTION:
{question}

Return your answer in this format:

Answer:
[Your answer]

Citations:
- [Title] - [File name]

Relevant Snippets:
- [Brief supporting snippet]
"""

    answer = call_groq(prompt)

    citations = []
    snippets = []

    for doc in docs:
        citations.append(
            {
                "title": doc.metadata.get("title", "Unknown title"),
                "source": doc.metadata.get("source", "Unknown source"),
            }
        )

        snippets.append(doc.page_content[:300])

    return {
        "question": question,
        "answer": answer,
        "citations": citations,
        "snippets": snippets,
    }