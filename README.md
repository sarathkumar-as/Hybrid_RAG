# Hybrid RAG Project

Ask questions about your own documents and see the source passages used in each answer. The app has a Streamlit interface, a FastAPI backend, Chroma for text search, and Neo4j for connections between concepts.

## What can I do with it?

- Upload and index PDF, DOCX, TXT, and Markdown files.
- Ask a question across all indexed files or select particular documents.
- Read an AI-generated answer and open its cited passages to check the evidence.
- View indexed documents and explore their concept links in the Knowledge Graph tab.

**Example:** Upload a policy PDF, click **Index documents**, and ask, “What are the eligibility requirements?” Open **Sources used in this answer** to check the relevant passages.

## How it works

| Step | What happens |
| --- | --- |
| 1. Index | You select 1–5 files and click **Index documents**. Selecting files alone does not index them. |
| 2. Prepare | The backend extracts text and splits it into smaller passages. |
| 3. Store | Chroma stores passages for similarity search. Neo4j stores documents, passages, concepts, and their links. |
| 4. Search | You ask a question. The app searches both stores and combines the matching passages. |
| 5. Answer | An OpenAI model drafts and checks an answer. The app shows citations such as `[S1]` alongside passages you can inspect. |

Here, **hybrid** means combining vector search with knowledge graph search. This project does not include BM25, live web search, cross-encoder reranking, or processing at terabyte scale. Citations help you verify answers; they do not guarantee accuracy.

![Diagram of document indexing and question answering](docs/architecture.png)

[View the editable architecture diagram](docs/architecture.mmd).

## Run it on your Windows computer

**You need:** Docker Desktop, an internet connection, and an OpenAI API key with API billing enabled. API usage is billed separately from a ChatGPT subscription. Allow at least 4 GB of memory for Docker as a starting point.

1. Open Docker Desktop and wait for its engine to start.
2. Open PowerShell in the project folder, where `docker-compose.yml` is located.
3. Create your private settings file:

   ```powershell
   Copy-Item .env.example .env
   ```

4. Open `.env` in a text editor. Set `OPENAI_API_KEY` and a strong `NEO4J_PASSWORD`. Save the file. Never commit or share `.env`.
5. Start the app:

   ```powershell
   docker compose up --build -d
   docker compose ps
   ```

6. Open [http://localhost:8501](http://localhost:8501). Upload a small document, click **Index documents**, ask a question in **Chat**, and open **Sources used in this answer**.

The API documentation is at [http://localhost:8000/docs](http://localhost:8000/docs). To check the backend in PowerShell, run `Invoke-RestMethod http://localhost:8000/health`.

To stop the app, run `docker compose down`. Your indexes remain in Docker volumes. **Do not run `docker compose down -v` unless you intend to delete the stored indexes.**

## Project files

| Location | Purpose |
| --- | --- |
| `frontend/app.py` | Upload, chat, document list, and graph interface |
| `backend/main.py` | API routes and input checks |
| `backend/service.py` | Indexing, search, and answer generation |
| `backend/core.py` | Text extraction and ranking helpers |
| `backend/config.py` | App settings |
| `docs/` | Architecture image and editable diagram |
| `tests/` | Core helper checks |
| `docker-compose.yml` | Local Docker setup |
| `docker-compose.traefik.yml` | VPS setup when Traefik already uses ports 80 and 443 |
| `docker-compose.vps.yml` and `deploy/Caddyfile` | VPS setup when ports 80 and 443 are free |
| `.env.example` | Settings template; put actual secrets in `.env` |

## Put the project on GitHub

GitHub displays and tracks the extracted project files. It does not run the app.

1. Create a **new, empty repository** on GitHub. Leave its README and `.gitignore` options unchecked because this project already has them.
2. Open PowerShell in the project folder. Check the files with `Get-ChildItem -Force`.
3. If the folder is **not already a Git repository**, run the following commands one at a time. Replace the example address with your repository URL:

   ```powershell
   git init
   git branch -M main
   git add .
   git diff --cached --name-only
   git commit -m "Add Hybrid RAG project"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
   git push -u origin main
   ```

4. Before committing, inspect the file list from `git diff --cached --name-only`. Make sure `.env`, private documents, `.venv/`, and local data are **absent**. If a secret appears, remove it from the staged files and rotate any key that has been exposed.
5. Refresh your GitHub repository page. Check that this README, `backend/`, `frontend/`, `docs/`, and Compose files are visible.

**If the project is already connected to GitHub**, keep that repository and use `git status`, `git add .`, `git diff --cached --name-only`, `git commit -m "Update Hybrid RAG project"`, and `git push`. Do not run `git init` or add `origin` again. Never use `git push --force` to resolve an ordinary push error.

## Deploy on a VPS

Choose the Compose file that matches the server:

| Server setup | File to use |
| --- | --- |
| Traefik already manages HTTPS on ports 80/443, such as a VPS also hosting n8n | `docker-compose.traefik.yml` |
| Ports 80/443 are free and this project should serve HTTPS through Caddy | `docker-compose.vps.yml` |

On the VPS, install Docker and its Compose plugin, copy or clone the project, and create `.env` from `.env.example`. Set `OPENAI_API_KEY`, `NEO4J_PASSWORD`, your domain, and the login settings required by your selected Compose file. Point the domain's DNS A record to the VPS and allow inbound ports 80/443. **Keep the existing Traefik and n8n services running** if you use the Traefik option.

From the project directory, replace `COMPOSE_FILE` with the selected filename:

```bash
docker compose -f COMPOSE_FILE config --quiet
docker compose -f COMPOSE_FILE up --build -d
docker compose -f COMPOSE_FILE ps
```

For the Traefik option, set `RAG_BASIC_AUTH` to a valid `username:hash` value in `.env`. For the Caddy option, set `RAG_USER` and `RAG_PASSWORD_HASH`. A hash is different from the password you type when signing in. Check DNS, HTTPS routing, and the login before uploading real documents. Keep `.env` and Docker volumes safe during updates; `down -v` deletes indexed data.

## API at a glance

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Check backend readiness |
| `GET /documents` | List indexed documents |
| `POST /documents` | Index 1–5 uploaded documents |
| `POST /ask` | Ask a question across all documents or selected document IDs |
| `GET /knowledge-graph/summary` | Get graph counts |
| `GET /knowledge-graph/entities`, `/relationships`, `/links` | Browse graph records |

See the interactive API details at `/docs` while the backend is running.

## Important limits

- Each upload accepts up to five files of 20 MB each. PDFs are limited to 100 pages and 150 passages by default.
- Scanned PDFs need OCR first. Complex page layouts and tables may extract imperfectly. TXT and Markdown files should use UTF-8.
- Extracted text and embeddings remain in Docker volumes; the app sends content to OpenAI for processing. Check your data policy before uploading confidential files.
- There is no document deletion button or separate account for each user in this starter project.
- For important decisions, compare the answer with the original document and cited passages.

## Troubleshooting

| Problem | Try this |
| --- | --- |
| Local page does not open | Check Docker Desktop and run `docker compose ps`. |
| Indexing or answering fails | Check your API key and run `docker compose logs --tail=100 backend neo4j`. |
| VPS domain does not open | Check DNS, firewall ports 80/443, selected Compose file, and proxy logs. |
| Want to update the app | Keep the existing `.env` and volumes; run `docker compose up --build -d` with the same Compose file. |

For development checks with Python 3.11, install the backend requirements and pytest, then run `python -m pytest -q` from the project folder.
