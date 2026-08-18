import os

from langsmith import traceable


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
def rag_pipeline(question):

    documents = retrieve_documents(question)

    answer = generate_answer(
        question,
        documents
    )

    return answer


question = "Does international travel require approval?"

answer = rag_pipeline(question)

print(answer)