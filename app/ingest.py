import os
import random
from pathlib import Path

import numpy as np
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


load_dotenv()

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

DATA_DIR = os.getenv("DATA_DIR", "data")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "chroma_db")


def load_documents(data_dir: str):
    documents = []

    for file_path in Path(data_dir).glob("*"):
        if file_path.suffix.lower() not in [".md", ".txt"]:
            continue

        text = file_path.read_text(encoding="utf-8")

        if not text.strip():
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": file_path.name,
                    "title": file_path.stem.replace("_", " ").title(),
                },
            )
        )

    return documents


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n## ", "\n### ", "\n\n", "\n", ".", " "],
    )

    return splitter.split_documents(documents)


def build_index():
    print("Loading documents...")
    documents = load_documents(DATA_DIR)

    print(f"Loaded {len(documents)} documents.")

    if not documents:
        raise ValueError(
            f"No documents found in {DATA_DIR}. Add .md or .txt policy files before indexing."
        )

    print("Chunking documents...")
    chunks = chunk_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    print("Creating embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Storing chunks in ChromaDB...")
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR,
    )

    print("Indexing complete.")


if __name__ == "__main__":
    build_index()