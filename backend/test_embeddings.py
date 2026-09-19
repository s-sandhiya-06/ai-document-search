from embeddings import generate_embeddings

texts = [
    "Electric vehicles use batteries for energy.",
    "Dijkstra's algorithm finds shortest paths in a graph.",
    "Python is a programming language."
]

embeddings = generate_embeddings(texts)

print("Number of embeddings:", len(embeddings))
print("Vector size:", len(embeddings[0]))
print("First few values:", embeddings[0][:5])