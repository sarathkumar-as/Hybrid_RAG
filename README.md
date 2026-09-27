# Hybrid RAG Chat System

Ask questions about your documents and inspect the passages used to answer them. The app combines **vector search** with a **knowledge graph**, then uses OpenAI to write an answer with source references.

**Live site:** [raghybrid.sbs](https://raghybrid.sbs)  
**Source code:** [Hybrid_RAG on GitHub](https://github.com/sarathkumar-as/Hybrid_RAG)

> The website is publicly accessible without a login prompt. Anyone with the address can use it and may see indexed content. Upload only material you are comfortable making available on this shared app. OpenAI API usage may incur charges.

## Start here: use the app

1. Open [https://raghybrid.sbs](https://raghybrid.sbs).
2. In the sidebar, choose **PDF**, **DOCX**, **TXT**, or **Markdown** files. Select up to **five files per upload**, each up to **20 MB** by default.
3. Click **Index documents**. Choosing a file alone does not store it. Wait for the success message.
4. Open **Chat**, choose all documents or specific documents, enter a question, and click **Find answer**.
5. Open **Sources used in this answer** to check the passages that support the answer.
6. Use **Documents** to see indexed files and **Knowledge Graph** to browse concepts and links.

For a first test, upload a short, non-sensitive document with a clear fact, then ask a question whose answer appears in that document. AI answers can be wrong; check the source text before relying on one.

## Architecture: from document to answer

![Hybrid RAG architecture showing document indexing, question answering, and source verification](docs/architecture.png)

The figure follows the three actions you take in the app:

1. **Add documents.** Click **Index documents** in the Streamlit website. FastAPI reads the files and splits their text into short passages. Chroma stores passages and OpenAI vectors; Neo4j stores document concepts and their links.
2. **Ask a question.** FastAPI searches both stores and brings together the most relevant passages. OpenAI uses those passages to draft an answer and check it against the retrieved evidence.
3. **Check the result.** Read the answer, open **Sources used in this answer**, and compare its claims with the original passages. A citation helps you verify an answer; it does not guarantee that the answer is correct.

| Part | Plain-English role |
| --- | --- |
| Streamlit frontend | The page for uploads, questions, documents, and graph browsing. |
| FastAPI backend | Reads documents, searches stored information, and prepares answers. |
| Chroma | Stores document passages and vector embeddings for similarity search. |
| Neo4j | Stores documents, passages, concepts, and their links. |
| OpenAI API | Creates embeddings and helps produce answers. Requires a separate API key and billing. |
| Docker Compose | Runs the app services together. |
| Traefik | Connects the public HTTPS domain to the frontend on the existing VPS. |

**Hybrid** in this version means vector search **plus** knowledge graph retrieval. The supplied code does not implement BM25, live web search, cross-encoder reranking, or terabyte-scale ingestion.

## Project folders

| File or folder | What it contains |
| --- | --- |
| `frontend/app.py` | Streamlit interface. |
| `backend/main.py` | FastAPI routes for uploads, questions, health, and graph data. |
| `backend/service.py` | Indexing, retrieval, and answer generation. |
| `backend/core.py` | Text extraction, chunking, and ranking helpers. |
| `backend/config.py` | App settings read from the environment. |
| `docs/architecture.png` | Illustrated three-step architecture guide used above. |
| `tests/test_core.py` | Core logic checks. |
| `docker-compose.yml` | Base services and local port mappings. |
| `docker-compose.traefik.yml` | Traefik settings for the existing Hostinger VPS. |
| `docker-compose.vps.yml`, `deploy/Caddyfile` | Alternative deployment for a VPS where ports 80/443 are free. |
| `.env.example` | Example setting names; copy to `.env` and replace placeholders. |

## Run locally with Docker

These commands run from the project root: the folder containing `docker-compose.yml`.

1. Install Docker Desktop or Docker Engine with Compose, then download or clone this repository.
2. Copy `.env.example` to `.env`. On Windows PowerShell use `Copy-Item .env.example .env`; on Linux/macOS use `cp .env.example .env`.
3. In `.env`, set at least `OPENAI_API_KEY` and a strong `NEO4J_PASSWORD`. Keep `.env` private.
4. Start the app:

   ```bash
   docker compose up --build -d
   docker compose ps
   ```

5. Open [http://localhost:8501](http://localhost:8501), index a test document, and ask a question.
6. If it does not start, run `docker compose logs --tail=80 backend frontend neo4j`.

The local backend health endpoint is `http://localhost:8000/health` where the base Compose file publishes port 8000. The initial build needs internet access and can take several minutes.

## Current Hostinger VPS deployment

The current server uses **Traefik** for HTTPS on `raghybrid.sbs`, and Traefik also serves **n8n**. The RAG services run under Compose project name **`hybrid-rag`** in `/opt/hybrid-rag`. Use the base Compose file together with its Traefik override. The Caddy deployment is a different option and must not be started alongside the existing Traefik on ports 80/443.

The deployed frontend's port 8501 is bound to `127.0.0.1`, so public visitors use [https://raghybrid.sbs](https://raghybrid.sbs) rather than the server IP and port. The Traefik basic-auth labels were removed for this public site. The server's private `.env` contains `RAG_DOMAIN=raghybrid.sbs` (hostname only; no `https://` or trailing slash).

### Update the code on the VPS

The repository must already be cloned at `/opt/hybrid-rag`. For a private repository, Git over HTTPS may request a personal access token instead of a GitHub password. Keep that token private.

1. Connect to the VPS and enter the project folder:

   ```bash
   cd /opt/hybrid-rag
   git status --short
   ```

2. Check any local changes before pulling. In particular, the **live** `docker-compose.yml` and `docker-compose.traefik.yml` contain VPS-specific edits; preserve them when updating from GitHub. Back up `.env` and the Docker volumes before a significant update.
3. Pull new code only after resolving local changes: `git pull --ff-only`. Do not overwrite the VPS files blindly.
4. Verify the Compose configuration without printing private values:

   ```bash
   docker compose -p hybrid-rag -f docker-compose.yml -f docker-compose.traefik.yml config --quiet
   ```

5. Rebuild and apply an **app code update** when ready:

   ```bash
   docker compose -p hybrid-rag -f docker-compose.yml -f docker-compose.traefik.yml up -d --build
   docker compose -p hybrid-rag -f docker-compose.yml -f docker-compose.traefik.yml ps
   ```

   For a frontend configuration change that does not require a rebuild, update only the frontend with `docker compose -p hybrid-rag -f docker-compose.yml -f docker-compose.traefik.yml up -d --no-deps --no-build frontend`.

**Do not run `docker compose down -v`** during updates: it deletes the saved Neo4j and Chroma volumes. Do not stop the separate n8n or Traefik services. Never commit `.env`, API keys, passwords, private documents, or database files to GitHub.

### Check the deployment

```bash
docker ps --filter name=hybrid-rag --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
curl -s -o /dev/null -w 'HTTP status: %{http_code}\n' https://raghybrid.sbs
docker compose -p hybrid-rag -f docker-compose.yml -f docker-compose.traefik.yml logs --tail=60 frontend backend
```

A `200` HTTP result means the homepage responded; it does not prove document indexing or answers work. Verify those features with a non-sensitive sample file in a fresh browser window.

| Symptom | First check |
| --- | --- |
| Site returns `404` | Ensure `RAG_DOMAIN` is exactly `raghybrid.sbs` and inspect the frontend Traefik `Host(...)` label. |
| Site returns `502` | Check whether the frontend is running and read Traefik logs. |
| Upload or question fails | Check backend and Neo4j status and backend logs. Verify the API key privately. |
| Browser asks for a username/password | Check whether the RAG router's Traefik basic-auth middleware was added back. |

## Limits and data handling

- By default, uploads are limited to five files per request and 20 MB per file; PDFs are also limited by `MAX_PAGES=100` and `MAX_CHUNKS=150`.
- Scanned PDFs need OCR before this app can read their text. Complex tables and multi-column layouts may extract imperfectly.
- Extracted passages, vectors, and graph data persist in Docker volumes. The starter app has no per-user document separation or document-deletion interface.
- The backend uses OpenAI services for indexing and answering. A ChatGPT subscription does not supply API credits.
- The application is a starter implementation. Test with small documents first and verify every answer against its cited sources.

## Developer check

From the project root with Python dependencies installed:

```bash
python -m pytest -q
```

The tests cover local core logic. Full indexing and answering also require Docker, Neo4j, and a valid OpenAI API key.
