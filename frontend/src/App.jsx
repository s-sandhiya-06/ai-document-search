import { useEffect, useRef, useState } from "react";
import "./App.css";

function App() {
  const [files, setFiles] = useState([]);
  const [message, setMessage] = useState("");
  const [question, setQuestion] = useState("");
const [selectedDocument, setSelectedDocument] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [documents, setDocuments] = useState([]);
  const answerRef = useRef(null);
 const loadDocuments = async () => {
  try {
    const response = await fetch(
      "http://127.0.0.1:8000/documents"
    );

    const data = await response.json();

    if (response.ok) {
      setDocuments(data.documents);
    }
  } catch (error) {
    console.log("Could not load documents.");
  }
};

useEffect(() => {
  loadDocuments();
}, []);
useEffect(() => {
  if (answer && answerRef.current) {
    answerRef.current.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }
}, [answer]);
  const uploadPDF = async () => {
    if (files.length === 0) {
      setMessage("Please select at least one PDF.");
      return;
    }
     setUploading(true);

    try {
      let uploadedFiles = [];

      for (const file of files) {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(
          "http://127.0.0.1:8000/upload",
          {
            method: "POST",
            body: formData,
          }
        );

        const data = await response.json();

        if (!response.ok) {
          setMessage(
            data.detail || `Failed to upload ${file.name}`
          );
          return;
        }

       if (data.duplicate) {
  setMessage(`${data.filename} is already uploaded.`);
  continue;

}

uploadedFiles.push(
  `${data.filename} (${data.chunks} chunks)`
);

setDocuments((previous) => [
  ...previous,
  {
    filename: data.filename,
    chunks: data.chunks,
    pages: data.pages,
  },
]);
      }

      if (uploadedFiles.length > 0) {
  setMessage(
    `Uploaded successfully: ${uploadedFiles.join(", ")}`
  );
}
await loadDocuments();

      setAnswer("");
      setSources([]);
    } catch (error) {
      setMessage("Could not connect to the backend.");
    }
    finally {
    setUploading(false);
  }
  };

  const askQuestion = async () => {
    
   if (!question.trim()) {
  setMessage("Please enter a question.");
  setAnswer("Please enter a question.");
  setSources([]);

  window.scrollTo({
    top: document.body.scrollHeight,
    behavior: "smooth",
  });

  return;
}
  setAnswer("");
  setSources([]);
  setMessage("");

    setLoading(true);
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/ask",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
          query: question,
          top_k: 5,
          filename: selectedDocument || null,
        }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setAnswer(data.answer);
        setSources(data.sources || []);

        setChatHistory((previous) => [
          ...previous,
          {
            question: question,
            answer: data.answer,
          },
        ]);

        setQuestion("");
      } else {
        setAnswer(
          data.detail || "Something went wrong."
        );
      }
    } catch (error) {
      setAnswer("Could not connect to the backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">

        {/* Header */}
        <header className="header">
          <h1>📄 AI Document Search</h1>
          <p>
            Upload PDFs and ask questions using AI
          </p>
        </header>

        {/* Upload Document */}
        <div className="card">
          <h2>Upload Documents</h2>

          <div className="upload-area">
  <input
    type="file"
    accept=".pdf"
    multiple
    onChange={(event) =>
      setFiles(
        Array.from(event.target.files)
      )
    }
  />

  <button
  onClick={uploadPDF}
  disabled={uploading}
>
  {uploading ? "Uploading..." : "Upload PDF"}
</button>
</div>

{files.length > 0 && (
  <div className="selected-files">
    <p>
      <strong>
        Selected Files ({files.length})
      </strong>
    </p>

    {files.map((file, index) => (
      <div
        className="selected-file"
        key={index}
      >
        📄 {file.name}
      </div>
    ))}
  </div>
)}

          {message && (
            <p
              className={
                message.startsWith("Uploaded")
                  ? "success"
                  : "error"
              }
            >
              {message}
            </p>
          )}
        </div>

        {/* Uploaded Documents */}
        {documents.length > 0 && (
          <div className="card">
            <h2>Uploaded Documents ({documents.length})</h2>
            <button
  onClick={async () => {
    const response = await fetch(
      "http://127.0.0.1:8000/clear",
      {
        method: "DELETE",
      }
    );

    if (response.ok) {
  setDocuments([]);
  setFiles([]);
  setSelectedDocument("");
  setMessage("All documents cleared successfully.");
  setAnswer("");
  setSources([]);
  setChatHistory([]);
  await loadDocuments();
}
  }}
>
  Clear Documents
</button>

            <div className="documents-list">
              {documents.map((document, index) => (
                <div
                  className="document-item"
                  key={index}
                >
                  <div>
  <strong>
    📄 {document.filename}
  </strong>

  <p>
    {document.pages} page
    {document.pages !== 1
      ? "s"
      : ""}{" "}
    · {document.chunks} chunks
  </p>
</div>

<button
  onClick={async () => {
    const response = await fetch(
      `http://127.0.0.1:8000/delete/${encodeURIComponent(
        document.filename
      )}`,
      {
        method: "DELETE",
      }
    );

    if (response.ok) {
      setDocuments((previous) =>
        previous.filter(
          (item) =>
            item.filename !== document.filename
        )
      );
      await loadDocuments();

      if (selectedDocument === document.filename) {
        setSelectedDocument("");
      }

      setMessage(
        `${document.filename} deleted successfully.`
      );
      setAnswer("");
      setSources([]);
    }
  }}
>
  Delete
</button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Ask Question */}
        <div className="card">
  <h2>Ask a Question</h2>

  <div className="document-selector">
    <label htmlFor="document-select">
      Ask about
    </label>

    <select
      id="document-select"
      value={selectedDocument}
      onChange={(event) =>
        setSelectedDocument(event.target.value)
      }
    >
      <option value="">
        All Documents
      </option>

      {documents.map((document, index) => (
        <option
          key={index}
          value={document.filename}
        >
          {document.filename}
        </option>
      ))}
    </select>
  </div>

  <div className="question-area">
            <input
              className="question-input"
              type="text"
              placeholder="What would you like to know?"
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  askQuestion();
                }
              }}
            />

            <button
              onClick={askQuestion}
              disabled={loading}
            >
              {loading ? "Thinking..." : "Ask"}
            </button>
          </div>
        </div>

        {/* Conversation */}
        {chatHistory.length > 0 && (
          <div className="card">
            <h2>Conversation</h2>

           <div className="chat-container">
            {chatHistory.map((chat, index) => (
              <div
                className="chat-item"
                key={index}
                ref={
                  index === chatHistory.length - 1
                    ? answerRef
                    : null
                }
              >
                  <div className="user-message">
                    <div className="chat-label">
                      You
                    </div>

                    <p>{chat.question}</p>
                  </div>

                  <div className="ai-message">
                    <div className="chat-label">
                      AI
                    </div>

                    <p>{chat.answer}</p>
                  </div>
                </div>
              ))}
              {answer === "Please enter a question." && (
  <div className="chat-item" ref={answerRef}>
    <div className="ai-message">
      <div className="chat-label">
        AI
      </div>
      <p>Please enter a question.</p>
    </div>
  </div>
)}
            </div>
          </div>
        )}

        {/* Loading */}
        

        {/* Sources */}
        {sources.length > 0 &&
  answer !== "I could not find the answer in the document." && (
          <div className="card">
            <h2>Sources</h2>

            {sources.map((source, index) => (
              <div
                className="source"
                key={index}
              >
                <strong>
                  Source {index + 1}
                </strong>

                <div className="source-document">
                  📄 {source.document}
                </div>

                <div className="source-page">
                  📄 Page {source.page} · Chunk {source.chunk}
                </div>
                <div className="source-score">
                  Relevance score: {source.score.toFixed(2)}
                </div>

                <p>{source.content}</p>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}

export default App;