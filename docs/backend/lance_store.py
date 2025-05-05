from pydantic import BaseModel
from lancedb.pydantic import LanceModel, Vector
from typing import List
from typing import Annotated
from pydantic import Field

class CodeChunk(LanceModel):
    id: str
    language: str
    startLine: int
    endLine: int
    imports: List[str]
    functions: List[str]
    embedding: Annotated[list[float], Field(dim=384)]  # ✅ CORRECT way

    model_config = {
        "protected_namespaces": ()
    }

def get_table():
    import lancedb
    db = lancedb.connect("./code-db")
    return db.create_table("code_chunks", schema=CodeChunk, mode="overwrite")
