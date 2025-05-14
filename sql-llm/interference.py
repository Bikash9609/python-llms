from transformers import pipeline

sql_pipeline = pipeline(
    "text-generation",
    model="./sql-expert",
    tokenizer="codellama/CodeLlama-7b-hf",
    device=0,
)

query = sql_pipeline(
    "Tables: products(id, name, price). Question: Show items under $500",
    max_new_tokens=100,
)
