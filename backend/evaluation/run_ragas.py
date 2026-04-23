import os
import json
import asyncio
import httpx
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, faithfulness, context_recall, context_precision
from core.config import get_settings
from core.security import create_access_token
import structlog
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

logger = structlog.get_logger(__name__)
settings = get_settings()

API_BASE = "http://localhost:8000/api/v1"

async def get_chat_response(question: str, role: str) -> dict:
    token = create_access_token(data={"sub": "eval_test", "role": role})
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE}/chat/stream",
            json={"message": question},
            headers={"Authorization": f"Bearer {token}"},
            timeout=120.0
        )
        
        final_answer = ""
        sources = []
        
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    if data["type"] == "done":
                         final_answer = data["final_answer"]
                         sources = data["sources"]
                except json.JSONDecodeError:
                    pass
                    
        return {
            "answer": final_answer,
            "contexts": [s.get("text", "") for s in sources]
        }

async def run_eval(dataset_path: str):
    logger.info("Loading dataset", path=dataset_path)
    with open(dataset_path, 'r') as f:
        qa_pairs = json.load(f)
        
    eval_dataset = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }
    
    for item in qa_pairs:
        logger.info("Evaluating item", id=item["id"], role=item["collection"])
        resp = await get_chat_response(item["question"], item["collection"])
        
        eval_dataset["question"].append(item["question"])
        eval_dataset["answer"].append(resp["answer"])
        eval_dataset["contexts"].append(resp["contexts"])
        eval_dataset["ground_truth"].append(item["ground_truth"])
        
    ds = Dataset.from_dict(eval_dataset)
    
    logger.info("Running RAGAs evaluation metrics")
    
    ragas_llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name="llama3-8b-8192")
    ragas_embeddings = FastEmbedEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    result = evaluate(
        ds,
        metrics=[answer_relevancy, faithfulness, context_recall, context_precision],
        llm=ragas_llm,
        embeddings=ragas_embeddings
    )
    
    output_path = f"backend/evaluation/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    logger.info("Evaluation complete", metrics=result)
    with open(output_path, 'w') as f:
        # Convert Ragas evaluate object to dict
        json.dump(result, f, indent=2)
        
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    args = parser.parse_args()
    
    asyncio.run(run_eval(args.dataset))
