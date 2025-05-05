from sentence_transformers import SentenceTransformer
from lance_store import get_table

table = get_table()
model = SentenceTransformer("all-MiniLM-L6-v2")

query = input("🔍 Ask something: ")
embedding = model.encode(query).tolist()
results = table.search(embedding).limit(3).to_df()

print("\n🔎 Top Matches:\n")
for i, row in results.iterrows():
    print(f"Chunk {i+1}:")
    print(f"Lines: {row['startLine']}–{row['endLine']}")
    print("Functions:\n", "\n---\n".join(row['functions'][:2]), "\n")
