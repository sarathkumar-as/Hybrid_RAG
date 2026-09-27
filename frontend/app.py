import os

import requests
import streamlit as st

API = os.getenv("API_URL", "http://backend:8000").rstrip("/")
st.set_page_config(page_title="Hybrid RAG Chat System", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
.block-container {max-width:1240px;padding-top:1.8rem;padding-bottom:2rem}
[data-testid="stSidebar"] {border-right:1px solid #283141}
[data-testid="stSidebar"] .block-container {padding-top:1.3rem}
h1,h2,h3 {letter-spacing:-.025em}
.hero {padding:10px 0 18px}
.hero h1 {font-size:2.25rem;margin:0;color:#f8fafc}
.hero p {margin:7px 0 0;color:#94a3b8}
.feature-card {background:#15283f;border:1px solid #254867;border-radius:16px;padding:20px 22px;color:#dbeafe}
.feature-card h3 {color:#58aaff;margin:0 0 14px}
.feature-card strong {color:#f1f5f9}
.feature-card li {margin:7px 0}
.step-card {padding:18px 8px;color:#dce5ef}
.step-card h2 {color:#f7f9fc;margin:0 0 14px}
.step-card li {margin:10px 0}
.sidebar-title {font-weight:750;font-size:1.1rem;color:#f8fafc;padding:4px 0 12px}
.hint {font-size:.87rem;color:#aab9ca}
div.stButton>button[kind="primary"],div.stFormSubmitButton>button[kind="primary"] {background:#2185e3;color:#fff;border-radius:10px}
[data-testid="stMetric"] {border:1px solid #303d51;border-radius:12px;padding:14px;background:#171e2b}
[data-testid="stChatMessage"] {border:1px solid #283549;border-radius:13px;background:#141b28}
</style>""", unsafe_allow_html=True)


def request_error(response):
    try:
        return response.json().get("detail", response.text)
    except ValueError:
        return response.text[:400]


try:
    health_response = requests.get(f"{API}/health", timeout=5)
    healthy = health_response.ok
    indexed = health_response.json().get("chunks", 0) if healthy else 0
except requests.RequestException:
    healthy, indexed = False, 0

graph_summary = None
if healthy:
    try:
        graph_response = requests.get(f"{API}/knowledge-graph/summary", timeout=12)
        if graph_response.ok:
            graph_summary = graph_response.json()
    except requests.RequestException:
        pass

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

indexed_documents = []
if healthy:
    try:
        docs_response = requests.get(f"{API}/documents", timeout=15)
        if docs_response.ok:
            indexed_documents = docs_response.json().get("documents", [])
    except requests.RequestException:
        pass

with st.sidebar:
    st.markdown('<div class="sidebar-title">⚙️ Settings & Info</div>', unsafe_allow_html=True)
    if healthy:
        st.success("Backend connected")
    else:
        st.error("Backend unavailable")
    with st.expander("Connection details"):
        st.write(f"FastAPI: {'Ready' if healthy else 'Unavailable'}")
        st.write(f"Neo4j: {'Connected (health check)' if healthy else 'Not verified'}")
        st.write(f"OpenAI: {'Key configured; API calls not checked' if healthy else 'Not verified'}")
        st.caption("Your API key stays in the server .env file. It is never entered in this browser.")
    st.divider()
    st.markdown("### 📥 Upload documents")
    st.caption("PDF, DOCX, TXT, and Markdown (.md). Up to 5 files per upload, 20 MB each.")
    files = st.file_uploader("Choose files", type=["pdf", "docx", "txt", "md"], accept_multiple_files=True, label_visibility="collapsed")
    if st.button("Index documents", type="primary", use_container_width=True, disabled=not healthy or not files):
        if len(files) > 5:
            st.error("Select at most five files per upload.")
        else:
            with st.spinner("Reading documents and building both search indexes…"):
                try:
                    response = requests.post(
                        f"{API}/documents",
                        files=[("files", (file.name, file.getvalue(), "application/octet-stream")) for file in files],
                        timeout=600,
                    )
                    if response.ok:
                        st.session_state.chat_history = []
                        st.session_state.upload_message = ", ".join(item["filename"] for item in response.json()["documents"])
                        st.rerun()
                    else:
                        st.error(request_error(response))
                except requests.RequestException as exc:
                    st.error(f"Upload connection error: {exc}")
    if st.session_state.get("upload_message"):
        st.success("Indexed: " + st.session_state.pop("upload_message"))
    st.divider()
    st.markdown("### 📊 Knowledge Base")
    if graph_summary:
        c1, c2 = st.columns(2)
        c1.metric("Documents", graph_summary["documents"])
        c2.metric("Chunks", graph_summary["chunks"])
        c3, c4 = st.columns(2)
        c3.metric("Entities", graph_summary["entities"])
        c4.metric("Relationships", graph_summary["relationships"])
        st.caption("Neo4j links: " + f"{graph_summary['has_chunk']} document–chunk · {graph_summary['mentions']} chunk–entity · {graph_summary['related_to']} concept–concept. Open the Knowledge Graph tab for details.")
    else:
        if healthy:
            st.warning("Knowledge graph counts unavailable. Check backend logs.")
        else:
            st.info("Knowledge graph unavailable until backend connects.")
    with st.expander("How it works"):
        st.markdown("1. Upload a document.\n2. Text becomes vector embeddings and graph concepts.\n3. Ask a question.\n4. Browse source evidence in the Knowledge Graph tab.")
    st.caption("Scanned PDFs need OCR. Uploaded document text is sent to the configured OpenAI API.")

st.markdown('<div class="hero"><h1>🧠 Hybrid RAG Chat System</h1><p>Ask grounded questions across your documents with vector and knowledge graph retrieval.</p></div>', unsafe_allow_html=True)
chat_tab, documents_tab, graph_tab = st.tabs(["💬 Chat", "📁 Documents", "🕸️ Knowledge Graph"])

with chat_tab:
    if not healthy:
        st.error("The backend is unavailable. Run `docker compose ps` and check the backend and Neo4j logs.")
    if not st.session_state.chat_history:
        left, right = st.columns([1.4, 1], gap="large")
        with left:
            st.markdown('<div class="step-card"><h2>📄 Getting started</h2><ol><li>Upload a document in the sidebar.</li><li>Wait for vector and graph indexing.</li><li>Ask a question. Explore graph evidence in the Knowledge Graph tab.</li></ol><h3>Supported formats</h3><p>📄 PDF &nbsp; 📝 DOCX &nbsp; 📃 TXT &nbsp; 📁 Markdown</p></div>', unsafe_allow_html=True)
        with right:
            st.markdown('<div class="feature-card"><h3>✨ Features</h3><strong>Hybrid retrieval</strong><ul><li>Semantic vector search</li><li>Knowledge graph concept lookup</li><li>Combined passage ranking</li></ul><strong>Grounded answers</strong><ul><li>Answers use retrieved document text</li><li>Source evidence in Knowledge Graph</li><li>Retrieval counts available per answer</li></ul></div>', unsafe_allow_html=True)
    else:
        head, action = st.columns([5, 1])
        with head:
            st.markdown("### Conversation")
        with action:
            if st.button("Clear chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        for turn in st.session_state.chat_history:
            with st.chat_message("user"):
                st.markdown(turn["question"])
            with st.chat_message("assistant"):
                st.markdown(turn["answer"])
                if turn.get("sources"):
                    with st.expander("Sources used in this answer"):
                        for source in turn["sources"]:
                            location = f" · page {source['page']}" if source.get("page") else ""
                            st.markdown(f"**[{source['label']}] {source['filename']}{location}**")
                            st.text(source["excerpt"])
                matches = turn["retrieval"]
                st.caption(f"Vector: {matches['vector_matches']} matches · Graph: {matches['graph_matches']} matches · {turn['elapsed_ms']} ms")
    st.divider()
    scope = st.radio("Search documents", ["All indexed documents", "Choose documents"], horizontal=True)
    chosen = []
    if scope == "Choose documents":
        options = {f"{doc['filename']} ({doc['document_id'][:8]})": doc["document_id"] for doc in indexed_documents}
        chosen = st.multiselect("Choose one or more indexed documents", list(options), default=list(options))
    with st.form("question_form", clear_on_submit=True):
        question = st.text_area("Ask a question", placeholder="What does the uploaded document say about…?", height=85)
        sent = st.form_submit_button("Find answer", type="primary", disabled=not healthy or indexed == 0)
    if sent:
        if len(question.strip()) < 3:
            st.warning("Type a question with at least three characters.")
        elif scope == "Choose documents" and not chosen:
            st.warning("Select at least one indexed document.")
        else:
            with st.spinner("Searching documents and preparing a cited answer…"):
                try:
                    request_data = {"question": question.strip()}
                    if scope == "Choose documents":
                        request_data["document_ids"] = [options[label] for label in chosen]
                    response = requests.post(f"{API}/ask", json=request_data, timeout=120)
                    if response.ok:
                        result = response.json()
                        st.session_state.chat_history.append({"question": question.strip(), **result})
                        st.rerun()
                    else:
                        st.error(request_error(response))
                except requests.RequestException as exc:
                    st.error(f"Query connection error: {exc}")

with documents_tab:
    st.markdown("### Indexed documents")
    st.caption("This list reflects the persistent vector index. Reupload the exact same file to refresh it.")
    if healthy:
        try:
            response = requests.get(f"{API}/documents", timeout=15)
            if response.ok:
                documents = response.json()["documents"]
                if not documents:
                    st.info("No documents indexed yet. Upload a file in the sidebar.")
                for doc in documents:
                    with st.container(border=True):
                        a, b = st.columns([4, 1])
                        a.markdown(f"**📄 {doc['filename']}**")
                        a.caption("PDF pages: " + str(doc["pages"]) if doc["pages"] is not None else "Text document")
                        b.metric("Passages", doc["chunks"])
            else:
                st.error(request_error(response))
        except requests.RequestException as exc:
            st.error(f"Could not load document list: {exc}")

with graph_tab:
    st.markdown("### Knowledge graph details")
    st.caption("Browse all live nodes and links from Neo4j, with their source documents and passages. RELATED_TO records a connection without naming a specific relationship type.")
    if graph_summary:
        metrics = st.columns(4)
        for box, (label, key) in zip(metrics, [("Documents", "documents"), ("Chunks", "chunks"), ("Entities", "entities"), ("Relationships", "relationships")]):
            box.metric(label, graph_summary[key])
        term = st.text_input("Search graph", placeholder="Filter by entity or concept", key="graph_search")
        breakdown = st.columns(3)
        breakdown[0].metric("Document → chunk", graph_summary["has_chunk"])
        breakdown[1].metric("Chunk → entity", graph_summary["mentions"])
        breakdown[2].metric("Entity → entity", graph_summary["related_to"])
        entity_tab, doc_link_tab, mention_tab, relation_tab = st.tabs(["Entities", "Document chunks", "Entity mentions", "Concept links"])

        def show_graph_rows(kind, page_key):
            page = st.number_input("Page number", min_value=1, step=1, key=page_key)
            try:
                endpoint = "links" if kind in ("document_chunks", "mentions") else kind
                params = {"search": term.strip(), "offset": (page - 1) * 50, "limit": 50}
                if endpoint == "links":
                    params["kind"] = kind
                response = requests.get(
                    f"{API}/knowledge-graph/{endpoint}",
                    params=params,
                    timeout=30,
                )
                if not response.ok:
                    st.error(request_error(response))
                    return
                result = response.json()
                st.caption(f"{result['total']} matching {kind}; showing up to 50 per page.")
                if not result["items"]:
                    st.info("No records on this page. Try page 1 or another search.")
                    return
                if kind == "entities":
                    rows = [{"Entity": item["name"], "Mentioned in chunks": item["mentions"], "Documents": ", ".join(item["documents"])} for item in result["items"]]
                elif kind == "relationships":
                    rows = [{"From entity": item["source"], "Connection": "RELATED_TO", "To entity": item["target"], "Document": item["document"], "Page": item["page"] if item["document"].lower().endswith(".pdf") else "—", "Evidence passage": item["evidence"]} for item in result["items"]]
                elif kind == "mentions":
                    rows = [{"Document": item["document"], "Chunk ID": item["chunk_id"], "Page": item["page"] if item["document"].lower().endswith(".pdf") else "—", "Entity": item["entity"], "Evidence passage": item["evidence"]} for item in result["items"]]
                else:
                    rows = [{"Document": item["document"], "Chunk ID": item["chunk_id"], "Page": item["page"] if item["document"].lower().endswith(".pdf") else "—", "Chunk text": item["evidence"]} for item in result["items"]]
                st.dataframe(rows, hide_index=True, use_container_width=True, height=440)
            except requests.RequestException as exc:
                st.error(f"Could not load graph details: {exc}")

        with entity_tab:
            show_graph_rows("entities", "entity_page")
        with doc_link_tab:
            show_graph_rows("document_chunks", "document_chunk_page")
        with mention_tab:
            show_graph_rows("mentions", "mention_page")
        with relation_tab:
            show_graph_rows("relationships", "relationship_page")
    elif healthy:
        st.warning("Knowledge graph details are unavailable. Check backend logs.")
    else:
        st.info("Start the backend and Neo4j to view graph details.")

st.markdown("<div style='text-align:center;color:#8392a9;font-size:.8rem;padding-top:22px'>Hybrid RAG · Streamlit · FastAPI · Chroma · Neo4j · OpenAI</div>", unsafe_allow_html=True)
