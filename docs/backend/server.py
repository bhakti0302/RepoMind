from fastapi import FastAPI, Request
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from .lance_store import get_table

app = FastAPI()
table = get_table()
model = SentenceTransformer("all-MiniLM-L6-v2")

class QueryRequest(BaseModel):
    query: str
    k: int = 3

@app.post("/search")
def search_code(req: QueryRequest):
    embedding = model.encode(req.query).tolist()
    results = table.search(embedding, vector_column_name="embedding").limit(req.k).to_df()
    print(table.schema())
    output = []
    for _, row in results.iterrows():
        output.append({
            "id": row["id"],
            "language": row["language"],
            "lines": f"{row['startLine']}-{row['endLine']}",
            "functions": row["functions"][:2],  # limit output
            "imports": row["imports"]
        })
    return {"matches": output}
