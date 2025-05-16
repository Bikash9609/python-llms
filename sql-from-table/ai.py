from db.init import run_query
from db import queries
import requests
import json

OLLAMA_MODEL = "DeepSeek-Coder:latest"
BASE_URL = "http://localhost:11434/api/generate"
meta = run_query(queries.get_table_meta_query(), fetch=True)
rels = run_query(queries.get_table_rels(), fetch=True)


def query_ollama_stream(prompt, model=OLLAMA_MODEL, context=None):
    data = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "context": context,
    }
    resp = requests.post(BASE_URL, json=data, stream=True)
    new_context = context
    for line in resp.iter_lines():
        if line:
            try:
                chunk = json.loads(line.decode("utf-8"))
                text = chunk.get("response", "")
                new_context = chunk.get("context", new_context)  # update context
                if text:
                    yield text
            except json.JSONDecodeError:
                continue
    # Optionally return the new_context if you want it outside streaming


def format_metadata(metadata, rels):
    output = "### Tables & Columns:\n"
    for row in metadata:
        table, column, data_type = row[:3]
        output += f"- {table}.{column} ({data_type})\n"

    output += "\n### Relationships (Foreign Keys):\n"
    for row in rels:
        src_table, src_col, tgt_table, tgt_col = row[1:5]
        output += f"- {src_table}.{src_col} → {tgt_table}.{tgt_col}\n"

    return output
