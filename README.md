# AI Document Search & RAG PDF Chatbot

An AI-powered document search and question-answering system that allows users to upload PDF documents and ask questions based on their contents.

The application uses Retrieval-Augmented Generation (RAG) to retrieve relevant sections from uploaded documents and generate answers using a local Large Language Model.

---

## Features

- Upload multiple PDF documents
- Ask natural-language questions about uploaded documents
- Document-specific question answering
- Semantic search using vector embeddings
- FAISS-based similarity search
- Local LLM using Ollama and Llama 3.2
- Grounded answers based only on retrieved document content
- Page and chunk information for retrieved sources
- Relevance scores for search results
- View uploaded documents
- Delete individual documents
- Clear all documents
- Duplicate document protection
- Persistent document storage
- Chat history during the current session
- Handles questions that cannot be answered from the documents
- Supports filenames containing spaces
- Modern responsive web interface

---

## Tech Stack

### Frontend
- React
- Vite
- JavaScript
- CSS

### Backend
- Python
- FastAPI
- Uvicorn

### AI / RAG
- Ollama
- Llama 3.2
- Sentence Transformers (`all-MiniLM-L6-v2`)
- FAISS

### Document Processing
- PyPDF

### Storage
- Pickle
- Local file storage

---

## System Architecture

```text
                    User
                     |
                     v
            React + Vite Frontend
                     |
                     | HTTP Requests
                     v
              FastAPI Backend
                     |
          +----------+----------+
          |                     |
          v                     v
    PDF Processing          Ollama LLM
          |                 (Llama 3.2)
          v
    Text Chunking
          |
          v
    Sentence Embeddings
          |
          v
        FAISS
          |
          v
  Relevant Document Chunks
          |
          v
      RAG Context
          |
          v
      Final Answer
```

---

## How It Works

### 1. Upload PDF

The user uploads a PDF through the React interface. The FastAPI backend:

1. Extracts text from the PDF.
2. Processes the document page by page.
3. Splits the text into smaller chunks.
4. Generates vector embeddings for the chunks.
5. Stores the embeddings in FAISS.
6. Saves document metadata for future use.

### 2. Ask a Question

The user enters a question, for example:

> What are my technical skills?

The system converts the question into an embedding and searches for relevant document chunks using FAISS.

### 3. Retrieve Relevant Information

The most relevant chunks are selected based on vector similarity. Each retrieved source contains:

- Document name
- Page number
- Chunk number
- Relevance score
- Retrieved text

### 4. Generate the Answer

The retrieved document content is provided to the local Llama 3.2 model through Ollama. The model is instructed to answer only using the retrieved document information.

If the required information is not found, the system responds:

> I could not find the answer in the document.

This helps reduce unsupported or hallucinated answers.

---

## RAG Pipeline

```text
PDF
 |
 v
Text Extraction
 |
 v
Chunking
 |
 v
Embedding Generation
 |
 v
FAISS Vector Store
 |
 v
Question
 |
 v
Question Embedding
 |
 v
Similarity Search
 |
 v
Relevant Chunks
 |
 v
LLM Context
 |
 v
Grounded Answer
```

---

## Project Structure

```text
ai-document-search/
│
├── backend/
│   ├── main.py
│   ├── document_store.py
│   ├── chunker.py
│   ├── embeddings.py
│   ├── llm.py
│   ├── vector_store.py
│   ├── requirements.txt
│   ├── test_embeddings.py
│   ├── test_llm.py
│   ├── test_search.py
│   ├── test_vector_store.py
│   ├── .gitignore
│   │
│   ├── storage/
│   └── uploads/
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── .gitignore
│
└── README.md
```

---

## Requirements

Make sure the following are installed:

- Python 3.10+
- Node.js
- npm
- Ollama
- Git

You also need the Ollama model:

```bash
ollama pull llama3.2:3b
```

---

## Backend Setup

Open PowerShell and go to the backend folder:

```powershell
cd C:\Users\sandhiya\ai-document-search\backend
```

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```powershell
pip install -r requirements.txt
```

Start the backend:

```powershell
uvicorn main:app --reload
```

The backend will run at:

```
http://127.0.0.1:8000
```

API documentation is available at:

```
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

Open another PowerShell terminal:

```powershell
cd C:\Users\sandhiya\ai-document-search\frontend
```

Install dependencies:

```powershell
npm install
```

Start the frontend:

```powershell
npm run dev
```

Then open the local URL displayed by Vite in the terminal.

---

## Example Questions

After uploading a document, users can ask questions such as:

- What are the technical skills?
- What projects are mentioned?
- What certifications are listed?
- What information is available on page 2?

The system retrieves relevant document sections before generating the answer.

---

## Document Grounding

The chatbot is designed to avoid generating information that is not supported by the uploaded document.

If relevant information cannot be retrieved, the system returns:

> I could not find the answer in the document.

Retrieved sources are displayed along with their page, chunk, and relevance information so that users can understand where the answer came from.

---

## Persistence

Uploaded documents and their vector data are stored locally so that documents remain available after restarting the backend.

Temporary/generated files such as:

```
venv/
node_modules/
uploads/
storage/
__pycache__/
```

are excluded from Git using `.gitignore`.

---

## Testing

The project contains backend tests for:

- Embedding generation
- LLM responses
- Search functionality
- Vector store functionality

The application was also tested for:

- Multiple document retrieval
- Document-specific retrieval
- Unrelated questions
- Empty questions
- Duplicate uploads
- Document deletion
- Clearing all documents
- Persistence after backend restart
- Filenames containing spaces

---

## Future Enhancements

Possible future improvements include:

- User authentication
- Cloud deployment
- Support for additional document formats
- Improved document ranking
- Semantic re-ranking
- Conversation persistence
- Multi-user document isolation
- More advanced RAG techniques

---

## Author

**Sandhiya S**

B.Tech Computer Science and Engineering  
VIT Chennai

GitHub: [s-sandhiya-06](https://github.com/s-sandhiya-06)