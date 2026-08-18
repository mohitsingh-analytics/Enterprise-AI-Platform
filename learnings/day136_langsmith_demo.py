from langsmith import traceable
from langsmith import Client


client = Client()


@traceable
def retrieve_documents(question):

    documents = [
        {
            "document_id": "DOC-001",
            "chunk_id": "CHUNK-001",
            "score": 0.94,
            "text": "International travel requires manager approval before booking."
        },
        {
            "document_id": "DOC-003",
            "chunk_id": "CHUNK-002",
            "score": 0.31,
            "text": "Business expenses must be submitted within 30 days."
        }
    ]

    return documents


@traceable
def generate_answer(question, context):

    return f"Answer generated using context: {context}"


@traceable
def rag_pipeline(inputs):

    question = inputs["question"]

    documents = retrieve_documents(question)

    answer = generate_answer(
        question,
        documents
    )

    return {
        "answer": answer
    }


def evaluate_answer(run, example):

    actual_answer = run.outputs["answer"]

    expected_answer = example.outputs["answer"]

    score = (
        actual_answer.strip().lower()
        == expected_answer.strip().lower()
    )

    return {
        "key": "answer_correct",
        "score": 1 if score else 0
    }


results = client.evaluate(
    rag_pipeline,
    data="ai-architect-rag-evaluation",
    evaluators=[evaluate_answer],
    experiment_prefix="day136-rag-baseline"
)

print(results)