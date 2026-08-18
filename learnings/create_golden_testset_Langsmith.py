import os

from langsmith import traceable
from langsmith import Client
from langsmith.evaluation import evaluate   

client = Client()
dataset = client.create_dataset(
    dataset_name="ai-architect-rag-evaluation",
    description="Golden dataset for RAG evaluation"
)

examples = [
    {
        "question": "Does international travel require approval?",
        "answer": "International travel requires manager approval before booking."
    },
    {
        "question": "How many days can employees work from home?",
        "answer": "Employees can work from home up to three days per week."
    },
    {
        "question": "When must business expenses be submitted?",
        "answer": "Business expenses must be submitted within 30 days."
    }
]

for example in examples:

    client.create_example(
        inputs={
            "question": example["question"]
        },
        outputs={
            "answer": example["answer"]
        },
        dataset_id=dataset.id
    )

