# Design and Evaluation

## Project Overview

PolicyPilot AI is a Retrieval-Augmented Generation application designed to answer questions about Kenya Aviation Limited’s data protection policy corpus. The corpus includes policies and procedures covering data protection principles, privacy notices, cookies, data retention, data subject rights, and data breach response.

## Corpus

The source corpus was prepared from Kenya Aviation Limited’s Data Protection Policies and split into multiple policy files:

1. Data Protection Policy
2. Website Privacy Policy
3. Customer Privacy Policy
4. Cookie Policy
5. Data Retention Policy
6. Data Subject Rights Policy
7. Data Breach Policy and Procedures
8. Data Retention Schedule
9. Data Subject Request Procedures
10. Breach Notification Templates

This structure was selected because the original document already contained distinct policy chapters and procedures.

## Design Choices

### Chunking

The documents were chunked using a heading-aware recursive text splitter. This was chosen because policies are naturally structured using chapters, sections, and subsections.

### Embeddings

The project uses `sentence-transformers/all-MiniLM-L6-v2` because it is free, lightweight, and suitable for semantic similarity search.

### Vector Store

ChromaDB was selected because it is lightweight, local, and appropriate for a student RAG project.

### Retrieval

The application uses top-k retrieval with k=4. This balances retrieval quality and response latency.

### Prompting

The prompt instructs the LLM to answer only from retrieved policy context, cite the relevant source document, avoid legal advice, and refuse questions outside the corpus.

## Evaluation

The evaluation set contains 20 questions across the following policy topics:

- Data protection principles
- Data subject rights
- Data breach reporting
- Data retention
- Cookies
- Third-party processors
- International transfers
- Security controls
- Privacy notices

The required metrics are:

- Groundedness
- Citation accuracy
- Latency p50 and p95