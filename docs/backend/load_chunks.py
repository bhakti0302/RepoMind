import os, json
from sentence_transformers import SentenceTransformer
from lance_store import get_table
from uuid import uuid4

table = get_table()
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed(chunk):
    text = " ".join(chunk["imports"] + [fn["code"] for fn in chunk["functions"]])
    return model.encode(text).tolist()

records = []
for file in os.listdir("debug_chunks"):
    if not file.endswith(".json"): continue
    with open(f"debug_chunks/{file}") as f:
        chunk = json.load(f)
        record = {
            "id": chunk["id"],
            "language": chunk["language"],
            "startLine": chunk["startLine"],
            "endLine": chunk["endLine"],
            "imports": chunk["imports"],
            "functions": [fn["code"] for fn in chunk["functions"]],
            "embedding": embed(chunk)
        }
        records.append(record)

table.add(records)
print(f"✅ Indexed {len(records)} chunks into LanceDB.")
