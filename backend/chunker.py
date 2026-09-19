def chunk_text(text, chunk_size=500, overlap=50, page_number=None):
    chunks = []

    paragraphs = text.split("\n")

    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        if len(current_chunk) + len(paragraph) + 1 <= chunk_size:
            current_chunk += paragraph + " "

        else:
            if current_chunk.strip():
                chunks.append({
                    "content": current_chunk.strip(),
                    "page": page_number
                })

            # Keep some previous text for context
            overlap_text = current_chunk[-overlap:] if current_chunk else ""

            current_chunk = overlap_text + paragraph + " "

    if current_chunk.strip():
        chunks.append({
            "content": current_chunk.strip(),
            "page": page_number
        })

    return chunks