from pydantic import BaseModel

class GuardrailResult(BaseModel):
    final_answer: str
    blocked: bool
    flags: list[str] = []
