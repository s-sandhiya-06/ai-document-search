from embeddings import generate_embeddings
import faiss
import numpy as np
import pickle
from pathlib import Path
MAX_DISTANCE = 1.70


class DocumentStore:
    def __init__(self):
        self.index = None
        self.chunks = []
        self.documents = []
        self.document_names = set()
        self.embeddings = []

    def add_document(self, chunks, filename):
        if filename in self.document_names:
            return False

        # Extract text from chunk objects
        texts = [chunk["content"] for chunk in chunks]

        embeddings = generate_embeddings(texts)

        vectors = np.array(embeddings).astype("float32")

        if self.index is None:
            dimension = vectors.shape[1]
            self.index = faiss.IndexFlatL2(dimension)

        self.index.add(vectors)

        self.chunks.extend(chunks)
        self.documents.extend([filename] * len(chunks))
        self.embeddings.extend(vectors)

        self.document_names.add(filename)

        return True

    def search(self, query, top_k=5, filename=None):
        if self.index is None:
            return []

        query_embedding = generate_embeddings([query])
        query_vector = np.array(query_embedding).astype("float32")

        # Specific document search
        if filename is not None:
            document_indices = [
                i for i, document in enumerate(self.documents)
                if document == filename
            ]

            if not document_indices:
                return []

            document_vectors = np.array(
                [self.embeddings[i] for i in document_indices]
            ).astype("float32")

            document_index = faiss.IndexFlatL2(
                document_vectors.shape[1]
            )

            document_index.add(document_vectors)

            top_k = min(top_k, len(document_indices))

            distances, local_indices = document_index.search(
                query_vector,
                top_k
            )
            results = []
            seen_content = set()
            for distance, local_i in zip(distances[0], local_indices[0]):
                if local_i >= 0:

                    if distance > MAX_DISTANCE:
                        continue

                    original_i = document_indices[local_i]
                    chunk = self.chunks[original_i]

                    if chunk["content"] in seen_content:
                        continue

                    seen_content.add(chunk["content"])

                    results.append({
                        "document": self.documents[original_i],
                        "content": chunk["content"],
                        "page": chunk["page"],
                        "chunk": chunk["chunk"],
                        "score": float(distance)
                    })
            return results

        # All documents
        top_k = min(top_k, len(self.chunks))

        distances, indices = self.index.search(
            query_vector,
            top_k
        )

        results = []
        seen_content = set()
        for distance, i in zip(distances[0], indices[0]):
            if i < len(self.chunks):

                if distance > MAX_DISTANCE:
                    continue

                chunk = self.chunks[i]

                if chunk["content"] in seen_content:
                    continue

                seen_content.add(chunk["content"])

                results.append({
                    "document": self.documents[i],
                    "content": chunk["content"],
                    "page": chunk["page"],
                    "chunk": chunk["chunk"],
                    "score": float(distance)
                })

        return results
    def delete_document(self, filename):
        if filename not in self.document_names:
            return False

        # Keep only chunks that do not belong to this document
        remaining_chunks = []
        remaining_documents = []
        remaining_embeddings = []

        for chunk, document, embedding in zip(
            self.chunks,
            self.documents,
            self.embeddings
        ):
            if document != filename:
                remaining_chunks.append(chunk)
                remaining_documents.append(document)
                remaining_embeddings.append(embedding)

        # Update stored data
        self.chunks = remaining_chunks
        self.documents = remaining_documents
        self.embeddings = remaining_embeddings
        self.document_names.remove(filename)

        # Rebuild FAISS index
        if self.embeddings:
            vectors = np.array(self.embeddings).astype("float32")

            self.index = faiss.IndexFlatL2(
                vectors.shape[1]
            )

            self.index.add(vectors)
        else:
            self.index = None

        return True
    def load(self):
        storage_path = Path(__file__).parent / "storage" / "document_store.pkl"

        if not storage_path.exists():
            return

        try:
            with storage_path.open("rb") as file:
                data = pickle.load(file)

            self.chunks = data["chunks"]
            self.documents = data["documents"]
            self.document_names = set(data["document_names"])
            self.embeddings = data["embeddings"]

            if self.embeddings:
                vectors = np.array(self.embeddings).astype("float32")
                self.index = faiss.IndexFlatL2(vectors.shape[1])
                self.index.add(vectors)

        except (pickle.PickleError, EOFError, KeyError, ValueError):
            self.index = None
            self.chunks = []
            self.documents = []
            self.document_names = set()
            self.embeddings = []
    def save(self):
        storage_path = Path(__file__).parent / "storage" / "document_store.pkl"
        storage_path.parent.mkdir(parents=True, exist_ok=True)

        backup_path = storage_path.with_suffix(".pkl.bak")

        if storage_path.exists():
            storage_path.replace(backup_path)

        data = {
            "chunks": self.chunks,
            "documents": self.documents,
            "document_names": self.document_names,
            "embeddings": self.embeddings
        }

        with storage_path.open("wb") as file:
            pickle.dump(data, file)
    def clear(self):
        self.index = None
        self.chunks = []
        self.documents = []
        self.document_names = set()
        self.embeddings = []