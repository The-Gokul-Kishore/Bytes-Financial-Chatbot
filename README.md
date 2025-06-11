![badge-labs](https://user-images.githubusercontent.com/327285/230928932-7c75f8ed-e57b-41db-9fb7-a292a13a1e58.svg)

# DTCC AI Hackathon 2025: Empowering India's Innovators
The purpose of hackathon is to leverage AI and ML Technologies to address critical challenges in the financial markets. The overall goal is to progress industry through Innovation, Networking and by providing effective Solutions.

**Hackathon Key Dates** 
•	June 6th - Event invites will be sent to participants
•	June 9th - Hackathon Open
•	June 9th-11th - Team collaboration and Use Case development
•	June 12th - Team presentations & demos
•	June 16th - Winners Announcement

More Info - https://communications.dtcc.com/dtcc-ai-hackathon-registration-17810.html

Commit Early & Commit Often!!!

Absolutely — here's a clean, well-structured, hackathon-ready comprehensive README for your project Bytes, incorporating everything you've shared so far.

You can paste this into your README.md file directly:

---

# Bytes – DTCC AI Hackathon 2025 Submission

An AI-powered financial insight assistant that enables users to query PDFs (like annual reports) using natural language.
Built using LangChain, PGVector, FastAPI, and Python agents, Bytes extracts tables, text, and embedded visuals from PDFs and responds with structured, explainable answers.

---

## Problem Statement
Self-Service Investigation (Chat NLP): Enable users to interact with data and perform investigations or analyses through conversational interfaces. Illustrative examples include ingesting corporate action data from multiple sources to extract key details, chatbot to provide market intelligence using capital markets data, and generate risk assessment reports from financial statements and regulatory filings.

---

## Tech Stack

| Layer          | Tools/Frameworks                            |
| -------------- | ------------------------------------------- |
| Language Model | LangChain                                   |
| Vector Store   | PostgreSQL with pgvector                    |
| Embeddings     | HuggingFace (MiniLM-L6-v2)                  |
| Backend API    | FastAPI + JWT Auth                          |
| PDF Parsing    | PyMuPDF (fitz), Camelot                     |
| Memory         | Custom LangChain Memory (PostgreSQL-backed) |
| CLI Tooling    | Typer + Rich                                |
| Packaging      | PEP 621 (pyproject.toml) via Hatch          |

---

## Team Composition

| Name         | Role                                       | Affiliation                               |
| ------------ | ------------------------------------------ | ----------------------------------------- |
| Ashika K     | Team Lead, AWS Integration & Risk Analysis | Chennai Institute of Technology (AI & DS) |
| Deepak J     | LLM Fine-Tuning & Agent Support            | Chennai Institute of Technology (AI & DS) |
| Gokul K      | AI Agent & Backend Development             | Chennai Institute of Technology (AI & DS) |
| Priya Reka S | Frontend Development                       | Chennai Institute of Technology (EC-ACT)  |
| Srisun S     | QA Engineering & Development Support       | Zoho Corporation                          |
| Darshini PG  | QA Engineering & Development Support       | Zoho Corporation                          |



---

##  Local Setup

### 1. Clone the Repo & Create a Virtual Environment

```bash
git clone https://github.com/your-team/bytes.git
cd bytes
uv venv  # or python -m venv .venv
uv sync  # or pip install -e .
```

### 2. Frontend Setup

```bash
cd frontend
npm install  # Install frontend dependencies
npm run dev  # Start the frontend development server
```

The frontend will be available at `http://localhost:5173`

### 3. Setup .env

Create a `.env` file at the project root:

```env
DB_USER=postgres
DB_PASSWORD=2005_Gokul
DB_NAME=vectordb
DB_HOST=localhost:5435
SECRET_KEY=supersecretkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 4. Start PostgreSQL with pgvector via Docker

```bash
docker run -d \
  --name bytes-pg \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=2005_Gokul \
  -e POSTGRES_DB=vectordb \
  -p 5435:5432 \
  ankane/pgvector
```

### 5. Initialize the Database

```bash
bytes init-db
```

Optionally, to delete and re-init:

```bash
bytes delete-db
bytes init-db
```

### 6. Start the Backend Server

```bash
bytes backend
```

The backend API will be available at `http://localhost:8000`

### 7. Access the Application

1. Open your browser and navigate to `http://localhost:5173`
2. Log in with your credentials
3. Start using the application!

---

## CLI Tooling

We provide a full CLI via Typer for setup and debugging.

### Example Commands

```bash
bytes init-db                            # Initialize database tables
bytes run-parser --load-path ./doc.pdf  # Parse PDF & embed to vector DB
bytes backend                            # Start FastAPI backend
bytes create-a-thread --thread-name Q1  # Create a chat thread
```

All CLI commands are defined in src/bytes/cli.py.

---

## Using DCO to sign your commits

**All commits** must be signed with a DCO signature to avoid being flagged by the DCO Bot. This means that your commit log message must contain a line that looks like the following one, with your actual name and email address:

```
Signed-off-by: John Doe <john.doe@example.com>
```

Adding the `-s` flag to your `git commit` will add that line automatically. You can also add it manually as part of your commit log message or add it afterwards with `git commit --amend -s`.

See [CONTRIBUTING.md](./.github/CONTRIBUTING.md) for more information

### Helpful DCO Resources
- [Git Tools - Signing Your Work](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)
- [Signing commits
](https://docs.github.com/en/github/authenticating-to-github/signing-commits)


## License

Copyright 2025 FINOS

Distributed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

SPDX-License-Identifier: [Apache-2.0](https://spdx.org/licenses/Apache-2.0)








