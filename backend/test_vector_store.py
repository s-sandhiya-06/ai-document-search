from embeddings import generate_embeddings
from vector_store import create_vector_store

texts = [
    "Electric vehicles use batteries for energy.",
    "Dijkstra's algorithm finds shortest paths in a graph.",
    "Python is a programming language."
]

embeddings = generate_embeddings(texts)

index = create_vector_store(embeddings)

print("Number of vectors stored:", index.ntotal)
print("Vector dimension:", index.d)