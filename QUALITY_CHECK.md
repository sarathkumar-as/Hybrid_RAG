# Quality check: Hybrid RAG

The score screenshot rated Automation 6/10, Reliability 5/10, Code Quality 4/10, and Documentation 6/10. Its comments said that the reviewer could see the upload and recent indexing but could not assess code from a UI screenshot. A numerical 10/10 score cannot be guaranteed by source changes.

| Area | Evidence in this package | How to confirm |
| --- | --- | --- |
| Automation | Upload indexes extracted passages in Chroma and graph concepts in Neo4j; Chat searches both. | Index a test document, open Documents and Knowledge Graph, and ask a matching question. |
| Reliability | All files in an upload batch are type/size checked before indexing starts; unsupported citation markers and uncited answer lines are rejected. | Try an invalid second file and confirm the first was not indexed; inspect answer citations. A failed external API call can still interrupt a batch. |
| Code quality | Focused tests cover heading search, ranking, citations, DOCX/Markdown extraction, and blank scanned PDFs. GitHub Actions runs these tests on push. | Check the GitHub Actions “Project checks” result and review `backend/`, `frontend/`, and `tests/`. |
| Documentation | README explains the app, actual public VPS setup, privacy, local startup, repository update, and verification. | Follow its local Docker instructions and compare the architecture diagram with the running app. |

## Hands-on acceptance checks

1. `docker compose up -d --build` and `docker compose ps`: verify Neo4j is healthy and the backend/frontend are running.
2. Open `http://localhost:8501`; confirm status is ready and saved counts load.
3. Upload a small TXT containing a unique sentence. Confirm Latest indexing run counts update and Documents contains its passages.
4. Ask a question answered explicitly in that sentence. Confirm `[S1]` points to the same text; check that an unrelated question abstains. An AI answer must still be checked by a person.
5. With a private admin token configured, delete the test document. Confirm it disappears from Documents and graph totals update. Never test Clear all against valuable data.
6. Refresh the site; saved indexes should persist in Docker volumes. Do not run `docker compose down -v`.

## Honest limitations

Tests in the repository are focused unit checks; they do not prove the full system works with a live OpenAI account, Docker volumes, public proxy, or every document. A public deployment permits anyone to upload and view indexed content; there is no per-user isolation. Citation formatting checks cannot prove a statement is true. Chroma and Neo4j are separate stores, so an external failure during writing can leave them out of sync. Full production reliability needs an isolated staging environment and repeatable integration tests.
