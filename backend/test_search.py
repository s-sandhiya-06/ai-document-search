from document_store import DocumentStore

texts = [
    "Electric vehicles use rechargeable batteries to store energy.",
    "Dijkstra's algorithm finds the shortest path between nodes.",
    "Python is a popular programming language used for software development.",
    "EV batteries have a limited driving range."
]

store = DocumentStore()

store.add_document(texts)

query = "How does an electric vehicle store energy?"

results = store.search(query, top_k=2)

print("\nSearch results:\n")

for i, result in enumerate(results, 1):
    print(f"Result {i}:")
    print(result)
    print()