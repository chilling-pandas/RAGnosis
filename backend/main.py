from fastapi import UploadFile, File
import os
from backend.services.pdf_service import PDFService


pdf_service = PDFService()


import json
from fastapi import FastAPI

app = FastAPI(title="Quiz AI Backend")

@app.get("/")
def root():
    return {"status": "Backend is running"}

@app.get("/health")
def health_check():
    return {"health": "OK"}


from backend.services.embedding_service import EmbeddingService
from backend.services.faiss_service import FaissService

embedding_service = EmbeddingService()
faiss_service = FaissService(dimension=384)



@app.post("/add-text")
def add_text(payload: dict):
    texts = payload["texts"]
    vectors = embedding_service.embed_texts(texts)
    faiss_service.add_vectors(vectors, texts)
    return {"message": "Texts added successfully"}

@app.post("/search")
def search_text(payload: dict):
    query = payload["query"]
    query_vector = embedding_service.embed_texts([query])
    results = faiss_service.search(query_vector)
    return {"results": results}

def quiz_prompt(context: str, difficulty: str):
    difficulty_rules = {
        "easy": "Ask simple definition-based questions.",
        "medium": "Ask conceptual questions that require understanding.",
        "hard": "Ask tricky questions involving edge cases, complexity, or pitfalls."
    }

    rule = difficulty_rules.get(difficulty.lower(), difficulty_rules["medium"])

    return f"""
You are a quiz generator.

Context:
{context}

Difficulty level: {difficulty.upper()}
Instructions: {rule}

Generate exactly 3 multiple-choice questions.

Return ONLY valid JSON in the following format:

{{
  "questions": [
    {{
      "question": "string",
      "options": [
        "Option 1 text",
        "Option 2 text",
        "Option 3 text",
        "Option 4 text"
      ],
      "correct_answer": "EXACT option text",
      "explanation": "string"
    }}
  ]
}}

Rules:
- Each option MUST be a meaningful answer, not letters
- correct_answer MUST exactly match one option
- Do NOT add markdown
- Do NOT add extra text
- Output must be valid JSON only
"""




from backend.services.llm_service import LLMService

llm_service = LLMService()




@app.post("/generate-quiz")
def generate_quiz(payload: dict):
    query = payload["topic"]
    difficulty = payload.get("difficulty", "medium")

    query_vector = embedding_service.embed_texts([query])
    retrieved_texts = faiss_service.search(query_vector)

    if not retrieved_texts:
        return {
            "error": "No knowledge found. Please add notes or upload a PDF first."
        }

    context = "\n".join(retrieved_texts)
    prompt = quiz_prompt(context, difficulty)

    quiz_text = llm_service.generate(prompt)

    try:
        quiz_json = json.loads(quiz_text)
        validated_questions = []

        for q in quiz_json.get("questions", []):
            options = q.get("options", [])
            correct = q.get("correct_answer")
        
            # validation checks
            if not options or correct not in options:
                continue  # skip invalid question
        
            validated_questions.append(q)
        
        if not validated_questions:
            return {
                "error": "Generated quiz is invalid. Please try again."
            }
        
        return {"questions": validated_questions}

    except Exception:
        return {
            "error": "LLM returned invalid JSON",
            "raw_output": quiz_text
        }
    
    return quiz_json


# pdf upload and quiz generate from uploaded pdf
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    os.makedirs("data", exist_ok=True)
    file_path = f"data/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = pdf_service.extract_text(file_path)

    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    vectors = embedding_service.embed_texts(chunks)
    faiss_service.add_vectors(vectors, chunks)

    return {
        "message": "PDF uploaded and indexed successfully",
        "chunks_added": len(chunks)
    }

#summarize pdf
def summary_prompt(context: str):
    return f"""
You are an academic assistant.

Based on the context below, generate a clear and concise summary.

Context:
{context}

Instructions:
- Summarize in 5–8 bullet points
- Keep it clear and structured
- Do not add information outside the context
"""
@app.post("/summarize")
def summarize(payload: dict):
    query = payload["topic"]

    query_vector = embedding_service.embed_texts([query])
    retrieved_texts = faiss_service.search(query_vector)

    if not retrieved_texts:
        return {"error": "No relevant content found."}

    context = "\n".join(retrieved_texts)
    prompt = summary_prompt(context)

    summary = llm_service.generate(prompt)

    return {"summary": summary}
