from io import BytesIO

from pypdf import PdfWriter

from docx import Document

from backend.core import citations_valid, clean_entities, document_chunks, fuse, heading_query, matching_heading_ids, pdf_chunks


def test_every_factual_line_requires_a_real_source():
    labels = {"[S1]", "[S2]"}
    assert citations_valid("- Vector search [S1]\n- Graph search [S2]", labels)
    assert not citations_valid("- Vector search [S1]\n- Invented claim", labels)
    assert not citations_valid("Invented claim [S9]", labels)
    assert not citations_valid("# Unsupported heading\nSupported detail [S1]", labels)


def test_short_heading_prioritizes_actual_section():
    assert heading_query("Backend:") == "Backend"
    assert heading_query("What does the backend do?") is None
    ids = ["unrelated", "answer"]
    documents = ["Frontend: renders pages. Backend mentioned later.",
                 "Backend:\n- Node.js + TypeScript\n- NestJS\nFrontend: UI"]
    assert matching_heading_ids("Backend:", ids, documents) == ["answer"]


def test_ranking_rewards_both_retrievers():
    assert fuse(["a", "b"], ["b", "c"])[0][0] == "b"


def test_clean_entities():
    assert clean_entities(["  FastAPI ", "fastapi", "Neo4j", None]) == ["fastapi", "neo4j"]


def test_blank_pdf_reports_ocr_requirement():
    writer = PdfWriter()
    writer.add_blank_page(width=400, height=400)
    stream = BytesIO()
    writer.write(stream)
    try:
        pdf_chunks(stream.getvalue(), "blank.pdf")
    except ValueError as exc:
        assert "OCR" in str(exc)
    else:
        raise AssertionError("Blank PDF should be rejected")


def test_docx_text_is_extracted_without_fake_page_numbers():
    doc = Document()
    doc.add_paragraph("The library service stores user playlists and saved albums.")
    stream = BytesIO()
    doc.save(stream)
    chunks = document_chunks(stream.getvalue(), "notes.docx")
    assert len(chunks) == 1
    assert "playlists" in chunks[0].text


def test_markdown_text_is_supported():
    chunks = document_chunks(b"# Design\n- Vector similarity\n- Graph entity relationships", "plan.md")
    assert len(chunks) == 1
    assert chunks[0].filename == "plan.md"
    assert "\n- Vector similarity\n- Graph entity relationships" in chunks[0].text
