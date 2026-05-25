import os
import requests
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "chroma_db")


OUT_OF_SCOPE_RESPONSE = (
    "I can only answer based on the Kenya Aviation Limited policy corpus available to me. "
    "I could not find this information in the provided policy documents."
)


SYSTEM_PROMPT = """
You are PolicyPilot AI, an assistant for Kenya Aviation Limited’s policy and procedure corpus.

Guardrails:
1. Answer only from the retrieved policy context provided to you.
2. Do not provide legal advice. Provide policy-based guidance only.
3. If the answer is not found in the retrieved context, say exactly:
   "I can only answer based on the Kenya Aviation Limited policy corpus available to me. I could not find this information in the provided policy documents."
4. Do not invent policy details, timelines, roles, penalties, procedures, or legal obligations.
5. Always cite the policy title and source file used to support the answer.
6. Include a short supporting snippet where possible.
7. Keep the answer concise, practical, and easy to understand.
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
    return vectorstore.similarity_search(question, k=k)


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

    if response.status_code != 200:
        print("Groq API error status:", response.status_code)
        print("Groq API error body:", response.text)
        response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]


def build_citations_and_snippets(docs):
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

    return citations, snippets


def answer_question(question: str):
    if not question or not question.strip():
        return {
            "question": question,
            "answer": "Please enter a policy question.",
            "citations": [],
            "snippets": [],
        }

    docs = retrieve_context(question, k=4)

    if not docs:
        return {
            "question": question,
            "answer": OUT_OF_SCOPE_RESPONSE,
            "citations": [],
            "snippets": [],
        }

    context = format_context(docs)

    prompt = f"""
Use the following retrieved policy context to answer the user's question.

POLICY CONTEXT:
{context}

USER QUESTION:
{question}

Instructions:
- Answer only using the policy context above.
- If the answer is not in the context, say exactly:
  "{OUT_OF_SCOPE_RESPONSE}"
- Cite the policy title and source file.
- Include relevant snippets.
- Do not provide legal advice.
- Do not invent details that are not present in the retrieved context.

Return your answer in this format:

Answer:
[Your answer]

Citations:
- [Title] - [File name]

Relevant Snippets:
- [Brief supporting snippet]
"""

    answer = call_groq(prompt)

    citations, snippets = build_citations_and_snippets(docs)

    if OUT_OF_SCOPE_RESPONSE in answer:
        citations = []
        snippets = []

    return {
        "question": question,
        "answer": answer,
        "citations": citations,
        "snippets": snippets,
    }