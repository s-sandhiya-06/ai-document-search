from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from pypdf import PdfReader
from chunker import chunk_text
from document_store import DocumentStore
from llm import answer_question
import shutil


class QuestionRequest(BaseModel):
    query: str
    top_k: int = 10
    filename: str | None = None


app = FastAPI(
    title="AI Document Search API",
    description="Backend for RAG-based PDF chatbot",
    version="0.1.0"
)


# Allow requests from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# Document store
document_store = DocumentStore()
document_store.load()


@app.get("/")
def read_root():
    return {
        "message": "AI Document Search API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }
@app.get("/documents")
def get_documents():

    documents = []

    for filename in sorted(document_store.document_names):

        document_chunks = [
            chunk
            for chunk, document in zip(
                document_store.chunks,
                document_store.documents
            )
            if document == filename
        ]

        pages = set(
            chunk["page"]
            for chunk in document_chunks
        )

        documents.append({
            "filename": filename,
            "pages": len(pages),
            "chunks": len(document_chunks)
        })

    return {
        "documents": documents
    }

@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):

    # Check file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # Save uploaded PDF
    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Read PDF
    reader = PdfReader(file_path)

    text = ""
    chunks = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

            page_chunks = chunk_text(
                page_text,
                page_number=page_number
            )

            for chunk_number, chunk in enumerate(page_chunks, start=1):
                chunk["chunk"] = chunk_number

            chunks.extend(page_chunks)

    # Add document to vector store
    added = document_store.add_document(
        chunks,
        file.filename
    )
    if added:
        document_store.save()
    if not added:
        return {
            "message": "Document already uploaded",
            "filename": file.filename,
            "pages": len(reader.pages),
            "chunks": len(chunks),
            "duplicate": True
        }
    return {
        "message": "PDF processed successfully",
        "filename": file.filename,
        "pages": len(reader.pages),
        "characters": len(text),
        "chunks": len(chunks),
        "duplicate": False
    }


@app.get("/search")
def search_document(query: str, top_k: int = 5):

    results = document_store.search(
        query,
        top_k=top_k
    )

    return {
        "query": query,
        "results": results
    }
@app.delete("/clear")
def clear_documents():

    document_store.clear()
    document_store.save()

    for file_path in UPLOAD_DIR.iterdir():
        if file_path.is_file():
            file_path.unlink()

    return {
        "message": "All documents cleared successfully"
    }
@app.delete("/delete/{filename}")
def delete_document(filename: str):

    deleted = document_store.delete_document(filename)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    document_store.save()

    file_path = UPLOAD_DIR / filename

    if file_path.exists():
        file_path.unlink()

    return {
        "message": "Document deleted successfully",
        "filename": filename
    }

@app.post("/ask")
def ask_question(request: QuestionRequest):

    query = request.query
    top_k = request.top_k
    filename = request.filename
    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    # Search for relevant document chunks
    results = document_store.search(
        query,
        top_k=top_k,
        filename=filename
    )

    # No documents uploaded
    if not results:
        if document_store.document_names:
            return {
                "query": query,
                "answer": "I could not find the answer in the document.",
                "sources": []
            }

        return {
            "query": query,
            "answer": "No document has been uploaded yet.",
            "sources": []
        }

    # Combine retrieved chunks for the LLM
    results.sort(key=lambda result: result["score"])

    context = "\n\n".join(
        f"[Source {index}]\n"
        f"Document: {result['document']}\n"
        f"Page: {result['page']}\n"
        f"Chunk: {result['chunk']}\n"
        f"{result['content']}"
        for index, result in enumerate(results, start=1)
    )

    # Generate answer using LLM
    answer = answer_question(
        query,
        context
    )

    return {
        "query": query,
        "answer": answer,
        "sources": results
    }