import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


load_dotenv()

DATA_DIR = os.getenv("DATA_DIR", "data")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "chroma_db")


def load_documents(data_dir: str):
    documents = []

    for file_path in Path(data_dir).glob("*"):
        if file_path.suffix.lower() == ".md" or file_path.suffix.lower() == ".txt":
            loader = TextLoader(str(file_path), encoding="utf-8")
            docs = loader.load()
        elif file_path.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(file_path))
            docs = loader.load()
        else:
            continue

        for doc in docs:
            doc.metadata["source"] = file_path.name
            doc.metadata["title"] = file_path.stem.replace("_", " ").title()

        documents.extend(docs)

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

    print("Chunking documents...")
    chunks = chunk_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    print("Creating embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Storing chunks in ChromaDB...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR,
    )

    vectorstore.persist()

    print("Indexing complete.")


if __name__ == "__main__":
    build_index()