from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai import format_metadata, meta, rels, query_ollama_stream
from typing import Optional


app = FastAPI()

# Allow requests from your frontend origin, e.g. localhost:5173 or 8080
origins = [
    "http://localhost:5173",  # adjust this to your Vue dev server origin
    "http://localhost:8000",  # backend itself (optional)
    "*",  # or allow all origins (not recommended for prod)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # allow all methods including OPTIONS
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str
    context: Optional[str] = None


@app.post("/ask")
async def ask(request: QuestionRequest):
    question = request.question
    prev_context = request.context

    formatted_schema = format_metadata(meta, rels)
    prompt = f"""
Given the following PostgreSQL schema:

{formatted_schema}

{question}
Be specific and list reasons.
"""

    # Event generator that updates context on the fly
    def event_generator():
        context = prev_context
        for chunk in query_ollama_stream(prompt, context=context):
            # chunk is just the text part, but context is updated internally in query_ollama_stream
            yield chunk

    return StreamingResponse(event_generator(), media_type="text/plain")
