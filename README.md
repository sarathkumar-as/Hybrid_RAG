# Hybrid RAG Project

Ask questions about your own documents and see the source passages used in each answer. The app has a Streamlit interface, a FastAPI backend, Chroma for text search, and Neo4j for connections between concepts.

<<<<<<< HEAD
## What can I do with it?
=======
> **Start here:** The steps below explain how to keep this project on GitHub and run it on Windows. Never upload `.env`, API keys, passwords, your Docker databases, or private source documents to GitHub.

## What this project does

1. You select one to five files (PDF, DOCX, TXT, or Markdown) and click **Index documents**. Uploading is an indexing step; choosing files alone does not index them.
2. FastAPI extracts readable text, separates it into passages, and requests OpenAI embeddings and concept extraction.
3. Chroma keeps passages and vectors; Neo4j keeps document, passage, and concept links. Both stores persist in Docker volumes.
4. In Chat, you search all indexed documents or choose specific ones and ask a question.
5. The backend retrieves matching passages using vector similarity and graph concepts, ranks them together, asks an OpenAI model for an answer, checks that answer, and returns citations you can inspect.

The name **hybrid** here means *vector retrieval plus knowledge graph retrieval*. This version does **not** implement BM25, web search, cross-encoder reranking, or terabyte-scale processing. It cannot guarantee a 100% correct answer; verify the cited source passage.

### Project folder map

| Path | Purpose | Put on GitHub? |
| --- | --- | --- |
| `README.md` | This guide, setup instructions, and project overview | Yes |
| `docs/architecture.png` | Complete upload and question flow diagram | Yes |
| `docs/architecture.mmd` | Editable Mermaid source for the diagram | Yes |
| `frontend/app.py` | Streamlit upload, chat, document, graph UI | Yes |
| `backend/main.py` | FastAPI routes and input validation | Yes |
| `backend/service.py` | Ingestion, Neo4j, Chroma, retrieval, answer generation | Yes |
| `backend/core.py` | Text extraction, chunking, ranking helpers | Yes |
| `backend/config.py` | Reads environment settings | Yes |
| `tests/test_core.py` | Checks for extraction and ranking helpers | Yes |
| `backend/requirements.txt`, `frontend/requirements.txt` | Python dependencies | Yes |
| `backend/Dockerfile`, `frontend/Dockerfile` | Container build instructions | Yes |
| `docker-compose.yml` | Local Windows deployment | Yes |
| `docker-compose.vps.yml`, `deploy/Caddyfile` | VPS with free ports 80/443; Caddy provides HTTPS and login | Yes |
| `docker-compose.traefik.yml` | VPS with existing Traefik on ports 80/443 | Yes |
| `.env.example` | Safe configuration template with placeholders | Yes |
| `.gitignore`, `.dockerignore` | Exclude local secrets and unnecessary files | Yes |
| `.env`, `.venv/`, `data/`, Docker volumes, private PDFs | Secrets and local data | **No** |

## A to Z: Put the complete project on GitHub (Windows PowerShell)

You need [Git for Windows](https://git-scm.com/downloads/win), a GitHub account, and this ZIP. Complete these steps on your **Windows computer**. If the project is already in a Git repository, read **Updating an existing GitHub repository** below instead of starting another repository.

### Part A — Prepare the local folder

1. Download `Hybrid_RAG_Project.zip` and extract it. Open the extracted **`hybrid-rag`** folder in File Explorer. This folder should contain `README.md`, `.gitignore`, and both Compose files. Enable **View → Show → File name extensions** in Windows if you cannot see `.md`.
2. In File Explorer, click the folder's address bar, type `powershell`, and press Enter. You should now see a prompt ending in `\hybrid-rag>`.
3. Check your tools and files:

   ```powershell
   git --version
   docker compose version
   Get-ChildItem -Force
   ```

   Install or open Docker Desktop later if Docker is not yet available. Do not put your OpenAI key in `README.md` or `.env.example`.

### Part B — Create an empty GitHub repository

4. Sign in at [github.com](https://github.com). Click **+ → New repository**. Enter `Hybrid_RAG_Project` (or another name you choose). Choose **Private** for a first deployment, especially if your documents or future commits might be sensitive. Click **Create repository**.
5. **Do not** check GitHub's boxes for a new README, `.gitignore`, or license: these files already exist locally. Copy your own repository HTTPS URL, for example `https://github.com/YOUR_USERNAME/Hybrid_RAG_Project.git`. Replace the example URL below with yours.

### Part C — Commit and upload

6. Run these commands in PowerShell, one line at a time. Replace the sample name, email, username, and repository address. Use the email associated with your GitHub commits.

   ```powershell
   git config --global user.name "YOUR NAME"
   git config --global user.email "YOUR_EMAIL@example.com"
   git init
   git branch -M main
   git status --short
git add README.md .gitignore .dockerignore .env.example docker-compose.yml docker-compose.vps.yml docker-compose.traefik.yml backend frontend deploy docs tests
   git status --short
   git diff --cached --name-only
   git commit -m "Add Hybrid RAG project and setup guide"
   git remote add origin https://github.com/YOUR_USERNAME/Hybrid_RAG_Project.git
   git push -u origin main
   ```

   **Before the commit**, inspect `git diff --cached --name-only`. It must show `.env.example` but **must not show `.env`** or private documents. If `.env` appears, stop and run `git restore --staged .env`. GitHub may open a browser sign-in window during the push; complete that sign-in rather than putting a password into the command.
7. Visit your repository's URL and refresh. Verify that `README.md` is shown on the repository home page and that the architecture picture appears below. Open `docs/architecture.png` and `backend/service.py` to check that the upload included the project, not just the README.

### Updating an existing GitHub repository

If you already have this project's local Git repository, **keep using that folder**. Back up your existing `.env`. Copy the updated `README.md`, `docs/`, `backend/`, `frontend/`, and other changed project files into it; keep any deliberate local deployment settings. In PowerShell from the existing repository:

```powershell
git status
git remote -v
git add README.md docs backend frontend .env.example docker-compose.yml docker-compose.vps.yml docker-compose.traefik.yml deploy .gitignore .dockerignore tests
git diff --cached --name-only
git commit -m "Update Hybrid RAG guide and architecture"
git push
```

If `git remote -v` is empty, add *your existing repository URL* with `git remote add origin YOUR_REPOSITORY_URL`, then use `git push -u origin main` if your branch is `main`. If `git status` says **nothing to commit**, your local files may not have been copied yet. If Git says **remote origin already exists**, do not run `git remote add origin` again. Do not use `git push --force` to fix an ordinary push error.

### Future changes and recovery

| Goal or symptom | What to do in PowerShell inside the project folder |
| --- | --- |
| Check what changed | `git status` |
| Save your next code or README change | `git add README.md docs backend frontend` → `git commit -m "Describe the change"` → `git push` |
| Download existing project onto a different PC | `git clone https://github.com/YOUR_USERNAME/Hybrid_RAG_Project.git`; then `cd Hybrid_RAG_Project` and create a fresh `.env` |
| GitHub says repository not found | Verify your URL, repository name, account access, and `git remote -v` |
| Push rejected because remote has new commits | First run `git pull --rebase origin main`, resolve any reported conflicts, then `git push` |
| `.env` appears in `git status` or a commit | Stop before pushing. Keep it ignored; if a real key reached GitHub, revoke and replace the key immediately |

GitHub stores code and documentation; it does **not** run the app. Run Docker locally or deploy on a VPS using the sections below. Uploading the ZIP to a repository is less useful than committing its **extracted files**, because GitHub then displays the README and tracks changes.

## Start on Windows with Docker Desktop
>>>>>>> 08439749de939355f9eb757ed9d569ad26ec6f04

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

<<<<<<< HEAD
![Diagram of document indexing and question answering](docs/architecture.png)
=======
## Hostinger VPS with existing Traefik and n8n (raghybrid.sbs)

On the inspected VPS, Traefik already binds ports 80 and 443, has the Docker provider enabled and a `letsencrypt` TLS resolver, and runs in host network mode. The separate n8n container must stay running. Use **`docker-compose.traefik.yml`** for this VPS. Do not run `docker-compose.vps.yml` here because its Caddy container would try to take the same ports. The project starts its own default Docker network; host-networked Traefik reaches the frontend by its container address through the Docker provider. No project database or app ports are published to the internet.

1. Download the current `Hybrid_RAG_Project.zip` to Windows. In PowerShell, change the path if needed and upload it over SSH (enter the VPS root password when requested):

   ```powershell
   scp "$env:USERPROFILE\Downloads\Hybrid_RAG_Project.zip" root@213.210.211.106:/tmp/Hybrid_RAG_Project.zip
   ```

2. Open the Hostinger browser terminal or connect by `ssh root@213.210.211.106`. Check available space with `df -h /` and memory with `free -h`. On the inspected VPS, approximately 93 GB of disk and 6.8 GiB of memory were available. In the VPS terminal, unpack the code:

   ```bash
   mkdir -p /opt/hybrid-rag
   unzip -o /tmp/Hybrid_RAG_Project.zip -d /opt
   cd /opt/hybrid-rag
   ls -a
   ```

   If `unzip` is missing, run `apt update` and `apt install -y unzip` first. Check that `docker-compose.traefik.yml` exists. Use this guide if the ZIP contains one `hybrid-rag` directory; inspect `unzip -l` first if the archive has been repacked.

3. Create secrets locally on the VPS and edit the configuration:

   ```bash
   cp .env.example .env
   chmod 600 .env
   nano .env
   ```

   Set `OPENAI_API_KEY` to a valid API platform key, `NEO4J_PASSWORD` to a long unique password, and `RAG_DOMAIN=raghybrid.sbs`. Do not share screenshots of `.env` or the API key. Leave the Caddy-only `RAG_PASSWORD_HASH` setting unused for this deployment. Save nano using Ctrl+O, Enter, Ctrl+X.

4. Generate a website password hash in the VPS terminal using `openssl passwd -apr1`. Type your new login password twice at the prompts. Copy only the resulting hash, which starts `$apr1$`. Edit `.env` again using `nano .env`; set `RAG_BASIC_AUTH='ragadmin:$apr1$YOUR_GENERATED_HASH'`, replacing the example with the **complete** output you copied. Keep the single quotes and record your login password privately. A password hash is not the password itself.

5. Confirm your DNS A record for `raghybrid.sbs` resolves to `213.210.211.106`, and that Hostinger's VPS firewall allows inbound TCP 80 and 443. From `/opt/hybrid-rag`, validate and start the stack:

   ```bash
   docker compose -f docker-compose.traefik.yml config --quiet
   docker compose -f docker-compose.traefik.yml up --build -d
   docker compose -f docker-compose.traefik.yml ps
   ```

   The first build may take several minutes. Open `https://raghybrid.sbs` and enter username `ragadmin` and your chosen website password. Index a small document, ask a question, and inspect its cited source passages. An answer cannot be guaranteed correct merely because it has citations.

6. For troubleshooting, run `docker compose -f docker-compose.traefik.yml logs --tail=80 frontend backend neo4j` from `/opt/hybrid-rag`, then `docker logs --tail=80 traefik-traefik-1` for routing/certificate errors. If the domain shows a Traefik 404, check the exact domain and labels with `docker inspect` on the frontend container. If the domain shows a 502, check frontend container health and Traefik's route to its Docker address. If a certificate fails, verify DNS, firewall access, and Traefik logs.

To update, back up `.env` and volumes, upload the latest ZIP, extract the project files, and repeat `docker compose -f docker-compose.traefik.yml up --build -d`. Keep `.env` private. Never run `docker compose down -v` during an update; `-v` deletes your Neo4j and Chroma volumes. Do not stop the existing n8n or Traefik containers.

## Publish on a Hostinger Ubuntu VPS with one domain (only when ports 80/443 are free)
>>>>>>> 08439749de939355f9eb757ed9d569ad26ec6f04

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

<<<<<<< HEAD
On the VPS, install Docker and its Compose plugin, copy or clone the project, and create `.env` from `.env.example`. Set `OPENAI_API_KEY`, `NEO4J_PASSWORD`, your domain, and the login settings required by your selected Compose file. Point the domain's DNS A record to the VPS and allow inbound ports 80/443. **Keep the existing Traefik and n8n services running** if you use the Traefik option.

From the project directory, replace `COMPOSE_FILE` with the selected filename:

```bash
docker compose -f COMPOSE_FILE config --quiet
docker compose -f COMPOSE_FILE up --build -d
docker compose -f COMPOSE_FILE ps
```
=======
![Hybrid RAG architecture: document indexing and question-answering paths](docs/architecture.png)

The image is stored in `docs/architecture.png`, and its editable flow definition is [docs/architecture.mmd](docs/architecture.mmd). GitHub displays the image automatically from this relative path when both the README and picture are committed. The upload path starts only when you click **Index documents**; the chat path starts when you click **Find answer**.

| Stage | Data going in | Work and result |
| --- | --- | --- |
| File upload | 1–5 PDF, DOCX, TXT, MD files | Browser sends files to the FastAPI `/documents` route |
| Text preparation | File bytes | Backend extracts text, preserves PDF page numbers, and cuts text into passages |
| Two indexes | Passages | OpenAI embeddings are stored in Chroma; extracted concepts and links are stored in Neo4j |
| Question | User question, optional selected document IDs | Backend embeds the question and extracts query concepts |
| Retrieval | Question vector and concepts | Chroma returns similar passages; Neo4j finds passages with matching concepts |
| Answer | Up to six fused passages | OpenAI drafts and reviews an answer, repairing missing citations if needed |
| Verification | Answer and cited passage text | Streamlit displays `[S1]` style citations and the **Sources used in this answer** expander |
>>>>>>> 08439749de939355f9eb757ed9d569ad26ec6f04

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
