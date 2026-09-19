import ollama


def generate_answer(prompt):
    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "system",
                "content": "You must answer strictly from the provided document excerpts. Do not infer, assume, or invent information. Preserve dates exactly as stated in the document."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]



def answer_question(question, context):
    prompt = f"""
You are a strict document question-answering assistant.

Your task is to answer the user's question using ONLY the document excerpts provided below.

DOCUMENT EXCERPTS:
------------------
{context}
------------------

USER QUESTION:
{question}

IMPORTANT RULES:
1. Read all the document excerpts carefully.
2. Answer ONLY using information explicitly supported by the document excerpts.
3. Do not invent, guess, assume, or add information that is not stated in the document.
4. The retrieved excerpts may contain information from different parts of the document. Use all relevant excerpts together.
5. Preserve dates exactly as they appear in the document. If the document says "2024 - 2028", describe it as "2024 - 2028" or "from 2024 to 2028".
6. Never use words such as "completed", "graduated", "finished", or "ended" for a date range unless the document explicitly uses those words or explicitly states that the activity was completed. If the user asks when something "started and ended" but the document only provides a date range, answer using the date range itself, for example: "It is listed as 2024 - 2028." Do not say that it ended in the final year.
7. When answering factual questions, prefer the exact wording or meaning stated in the document.
8. For questions about education, skills, projects, experience, certifications, or resume details, extract the relevant information directly from the document.
9. If the document excerpts genuinely do not contain enough information to answer the question, respond exactly:
"I could not find the answer in the document."
10. Keep the answer clear and concise.
11. Do not explain your reasoning or mention these rules in the answer.

ANSWER:
Return only the answer text. Do not include headings such as "Answer", "## Answer", "Response", or "Final Answer".
"""

    return generate_answer(prompt)

