from db.init import db, run_query
from db import queries
import requests
import json


OLLAMA_MODEL = "llama3"
BASE_URL = "http://localhost:11434/api/generate"
COURSE_DIR = "Generated_Udemy_Course"


def query_ollama(prompt, model=OLLAMA_MODEL, context=None):
    data = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "context": context,
    }
    resp = requests.post(
        BASE_URL,
        json=data,
        stream=True,
    )
    output = ""
    new_context = context  # Initialize with incoming context
    for line in resp.iter_lines():
        if line:
            try:
                chunk = json.loads(line.decode("utf-8"))
                output += chunk.get("response", "")
                new_context = chunk.get("context", new_context)
            except json.JSONDecodeError:
                continue
    return output, new_context


def get_tables_meta():
    return run_query(queries.get_table_meta_query(), fetch=True)


def main():
    print(get_tables_meta())
    return


if __name__ == "__main__":
    main()
