documents = [
    {
        "id": "DOC-001",
        "text": "International travel requires manager approval before booking."
    },
    {
        "id": "DOC-002",
        "text": "International travel reimbursement is limited to INR 50,000 per trip."
    },
    {
        "id": "DOC-003",
        "text": "Domestic travel reimbursement is limited to INR 25,000 per trip."
    },
    {
        "id": "DOC-004",
        "text": "Employees must submit business expenses within 30 days."
    },
    {
        "id": "DOC-005",
        "text": "Policy FIN-2024-17 section 4.2.3 defines international travel reimbursement."
    }
]

from rank_bm25 import BM25Okapi

tokenized_documents = [
    doc["text"].lower().split()
    for doc in documents
]

bm25 = BM25Okapi(tokenized_documents)
print(bm25.get_scores(["submit", "reimbursement"]))


def bm25_search(query, documents, top_n=3):
    tokens = query.lower().split()
    scores = bm25.get_scores(tokens)
    ranked= sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:top_n]

query = "FIN-2024-17 4.2.3"

results = bm25_search(query, documents)

print("\nBM25 results:")

for doc, score in results:
    print(f"{score:.3f} | {doc['id']} | {doc['text']}")

semantic_scores = {
    "DOC-001": 0.62,
    "DOC-002": 0.91,
    "DOC-003": 0.55,
    "DOC-004": 0.31,
    "DOC-005": 0.88
}

def vector_search(top_k=3):

    ranked = sorted(
        documents,
        key=lambda doc: semantic_scores[doc["id"]],
        reverse=True
    )

    return [
        (doc, semantic_scores[doc["id"]])
        for doc in ranked[:top_k]
    ]

print("\nVector results:")

for doc, score in vector_search():
    print(f"{score:.3f} | {doc['id']} | {doc['text']}")


def hybrid_search(query, top_k=3):

    bm25_results = bm25_search(query,documents, top_n=len(documents))
    vector_results = vector_search(top_k=len(documents))

    bm25_scores = {
        doc["id"]: score
        for doc, score in bm25_results
    }

    vector_scores = {
        doc["id"]: score
        for doc, score in vector_results
    }

    combined = []

    for doc in documents:

        bm25_score = bm25_scores.get(doc["id"], 0)
        vector_score = vector_scores.get(doc["id"], 0)

        final_score = (
            0.4 * bm25_score +
            0.6 * vector_score
        )

        combined.append(
            (doc, final_score)
        )

    return sorted(
        combined,
        key=lambda x: x[1],
        reverse=True
    )[:top_k]

print("\nHybrid results:")

for doc, score in hybrid_search(query):
    print(f"{score:.3f} | {doc['id']} | {doc['text']}")


reranker_scores = {
    "DOC-001": 0.40,
    "DOC-002": 0.98,
    "DOC-003": 0.20,
    "DOC-004": 0.10,
    "DOC-005": 0.85
}

def rerank(results, top_n=3):

    reranked = []

    for doc, _ in results:

        score = reranker_scores[doc["id"]]

        reranked.append(
            (doc, score)
        )

    return sorted(
        reranked,
        key=lambda x: x[1],
        reverse=True
    )[:top_n]


hybrid_results = hybrid_search(query)

final_results = rerank(
    hybrid_results,
    top_n=3
)

print("\nReranked results:")

for doc, score in final_results:

    print(
        f"{score:.3f} | "
        f"{doc['id']} | "
        f"{doc['text']}"
    )