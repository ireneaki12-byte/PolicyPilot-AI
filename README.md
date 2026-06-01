# PolicyPilot AI

PolicyPilot AI is a Retrieval-Augmented Generation (RAG) web application that answers questions about company policies and procedures.

For this project, the pilot policy corpus is based on Kenya Aviation Limited’s Data Protection Policy suite. The corpus covers data protection principles, privacy, cookie use, data retention, data subject rights, third-party processors, breach response, and related procedures.

PolicyPilot AI retrieves relevant policy sections from a ChromaDB vector database and uses a Large Language Model to generate grounded answers with citations and supporting snippets.

---

## Project Purpose

Company policies are often long and difficult to search manually. PolicyPilot AI helps users quickly ask natural-language questions such as:

- What should an employee do if they suspect a personal data breach?
- What are the rights of a data subject?
- Can employees share passwords?
- What types of cookies does the website use?
- Within how long should a breach be reported?

The goal is to reduce the risk of generic or hallucinated chatbot answers by grounding responses in retrieved policy content.

---

## Main Features

- RAG-based policy question answering
- Policy document ingestion and indexing
- Text chunking with overlap
- Semantic search using embeddings
- ChromaDB vector store
- Groq LLM integration
- Web-based chat interface
- Policy citations and supporting snippets
- Out-of-corpus refusal guardrail
- No-legal-advice guardrail
- Responsive UI for desktop, tablet, and mobile
- Katibu bird mascot
- `/chat` API endpoint
- `/health` endpoint
- Automated tests using pytest
- Evaluation script for groundedness, citation accuracy, and latency
- GitHub Actions CI workflow
- Render deployment support

---

## Technology Stack

| 
| Backend - Python & Flask 
| RAG framework - LangChain 
| Embeddings - HuggingFace Sentence Transformers 
| Embedding model - `sentence-transformers/all-MiniLM-L6-v2` 
| Vector database - ChromaDB 
| LLM provider - Groq 
| LLM model - `llama-3.1-8b-instant` |
| Testing - pytest 
| Deployment - Render
| CI/CD - GitHub Actions 

---

## Project Structure

```text
PolicyPilot-AI/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── ingest.py
│   ├── rag_pipeline.py
│   └── static/
│       ├── katibu.png
│       └── media/
│           └── katibu_bird_waving_hi.gif
│
├── data/
│   ├── data_protection_policy.md
│   ├── website_privacy_policy.md
│   ├── privacy_policy.md
│   ├── cookie_policy.md
│   ├── data_retention_policy.md
│   ├── data_subject_rights_policy.md
│   ├── data_breach_policy_and_procedures.md
│   ├── data_retention_schedule.md
│   ├── data_subject_request_procedures.md
│   └── breach_notification_templates.md
│
├── evaluation/
│   ├── eval_questions.csv
│   ├── run_evaluation.py
│   └── evaluation_results.csv
│
├── tests/
│   ├── test_health.py
│   ├── test_ingestion.py
│   └── test_rag.py
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .env.example
├── .gitignore
├── .python-version
├── requirements.txt
├── render.yaml
├── README.md
├── design-and-evaluation.md
├── rag-architecture.md
└── ai-tooling.md


## Running Locally

Follow these steps to run PolicyPilot AI on your local machine.

### a. Clone the repository

```bash
git clone https://github.com/ireneaki12-byte/PolicyPilot-AI.git
cd PolicyPilot-AI


***********************************************
## Running Locally

Follow these steps to run PolicyPilot AI on your local machine.

1. Clone the repository

```bash
git clone https://github.com/ireneaki12-byte/PolicyPilot-AI.git
cd PolicyPilot-AI
2. Create and activate a virtual environment

On Windows PowerShell:

py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1

3. Create a file called .env in the project root.

PolicyPilot-AI/
├── .env
├── requirements.txt
├── app/
├── data/
└── evaluation/

4. Add the following values:

GROQ_API_KEY=your_real_groq_api_key_here
LLM_MODEL=llama-3.1-8b-instant
CHROMA_DB_DIR=chroma_db
DATA_DIR=data

Do not commit .env to GitHub as it contains secrets.

5. Build the vector index

Run the ingestion script:
python app/ingest.py

6. Start the application

Run the Flask app as a module: python -m app.main
Open the app in your browser: http://127.0.0.1:5000

7. Test the health endpoint

Open:http://127.0.0.1:5000/health

Expected response:

{
  "app": "PolicyPilot AI",
  "status": "ok"
}

***********************************

Deploying on Render

PolicyPilot AI can be deployed on Render as a Python web service.

1. Prepare the repository
Before deploying, ensure the following files are committed to GitHub:
app/
data/
evaluation/
tests/
requirements.txt
render.yaml
.python-version
.env.example
README.md

Do not commit:

.env
.venv/
chroma_db/
__pycache__/

.gitignore should include:

.venv/
.env
.env.*
!.env.example
__pycache__/
*.pyc
chroma_db/
.pytest_cache/
2. Add Python version file

Create a file called .python-version in the project root.

PolicyPilot-AI/
├── .python-version
├── requirements.txt
├── render.yaml
└── app/

Inside .python-version, add:

3.11.9 - Python 3.11 is used because the RAG libraries are more stable on Python 3.11 than on newer Python versions.

3. Confirm render.yaml

Configure render.yaml file:

services:
  - type: web
    name: policypilot-ai
    env: python
    buildCommand: "python -m pip install --upgrade pip && python -m pip install --no-cache-dir -r requirements.txt && python app/ingest.py"
    startCommand: "gunicorn app.main:app"
    envVars:
      - key: GROQ_API_KEY
        sync: false
      - key: LLM_MODEL
        value: llama-3.1-8b-instant
      - key: CHROMA_DB_DIR
        value: chroma_db
      - key: DATA_DIR
        value: data
      - key: PYTHON_VERSION
        value: 3.11.9
4. Create a new Render web service
Go to Render.
Select New +.
Choose Web Service.
Connect your GitHub repository.
Select the PolicyPilot-AI repository.
Choose the branch, usually main.
5. Configure Render build settings

Use the following settings:
Environment: Python
Build Command:
python -m pip install --upgrade pip && python -m pip install --no-cache-dir -r requirements.txt && python app/ingest.py

Start Command:
gunicorn app.main:app

6. Add environment variables on Render
In Render, go to:
Service → Environment
Add:

GROQ_API_KEY=your_real_groq_api_key_here
LLM_MODEL=llama-3.1-8b-instant
CHROMA_DB_DIR=chroma_db
DATA_DIR=data
PYTHON_VERSION=3.11.9

7. Deploy

Click:
Manual Deploy → Clear build cache & deploy
Render should run the build command, install dependencies, ingest the policy documents, create the ChromaDB index, and start the Flask app using Gunicorn.

8. Verify deployment

After deployment, open the Render URL.
Test: https://your-render-url.onrender.com/

Then test the health endpoint: https://your-render-url.onrender.com/health

Expected response:

{
  "app": "PolicyPilot AI",
  "status": "ok"
}

