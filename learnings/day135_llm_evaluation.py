golden_dataset = [
    {
        "id": "Q001",
        "question": "Does international travel require approval?",
        "expected_answer": "International travel requires manager approval before booking.",
        "expected_context": "International travel requires manager approval before booking."
    },
    {
        "id": "Q002",
        "question": "How many days can employees work from home?",
        "expected_answer": "Employees can work from home up to three days per week.",
        "expected_context": "Employees can work from home up to three days per week."
    },
    {
        "id": "Q003",
        "question": "When must business expenses be submitted?",
        "expected_answer": "Business expenses must be submitted within 30 days.",
        "expected_context": "Employees must submit business expenses within 30 days."
    }
]



model_outputs = [
    {
        "id": "Q001",
        "answer": "International travel requires manager approval before booking.",
        "retrieved_context": "International travel requires manager approval before booking."
    },
    {
        "id": "Q002",
        "answer": "Employees can work remotely three days per week.",
        "retrieved_context": "Employees can work from home up to three days per week."
    },
    {
        "id": "Q003",
        "answer": "Business expenses should be submitted within 60 days.",
        "retrieved_context": "Employees must submit business expenses within 30 days."
    }
]


def exact_match(expected, actual):
    return expected.strip().lower() == actual.strip().lower()


for item in golden_dataset:

    output = next(
        x for x in model_outputs
        if x["id"] == item["id"]
    )

    result = exact_match(
        item["expected_answer"],
        output["answer"]
    )

    print(item["id"], result)



def token_overlap(expected, actual):
    expected_words = set(expected.strip().lower().split())
    actual_words = set(actual.strip().lower().split())
    if not expected_words:
        return 0
    common_words = expected_words.intersection(actual_words)
    return len(common_words) / len(expected_words)

for item in golden_dataset:

    output = next(
        x for x in model_outputs
        if x["id"] == item["id"]
    )

    score = token_overlap(
        item["expected_answer"],
        output["answer"]
    )

    print(
        item["id"],
        "Token overlap:",
        round(score, 2)
    )


import math

def cosine_similarity(expected, actual):
    expected_words = expected.strip().lower().split()
    actual_words = actual.strip().lower().split()

    # Create a set of unique words
    unique_words = set(expected_words).union(set(actual_words))

    # Create frequency vectors
    expected_vector = [expected_words.count(word) for word in unique_words]
    actual_vector = [actual_words.count(word) for word in unique_words]

    # Calculate dot product and magnitudes
    dot_product = sum(e * a for e, a in zip(expected_vector, actual_vector))
    magnitude_expected = math.sqrt(sum(e ** 2 for e in expected_vector))
    magnitude_actual = math.sqrt(sum(a ** 2 for a in actual_vector))

    if magnitude_expected == 0 or magnitude_actual == 0:
        return 0.0

    return dot_product / (magnitude_expected * magnitude_actual)

def fake_embedding(text):

    text = text.lower()

    return [
        text.count("travel"),
        text.count("approval"),
        text.count("employee"),
        text.count("home"),
        text.count("expense"),
        text.count("days"),
        text.count("international")
    ]

def semantic_similarity(expected, actual):
    expected_embedding = fake_embedding(expected)
    actual_embedding = fake_embedding(actual)

    dot_product = sum(e * a for e, a in zip(expected_embedding, actual_embedding))
    magnitude_expected = math.sqrt(sum(e ** 2 for e in expected_embedding))
    magnitude_actual = math.sqrt(sum(a ** 2 for a in actual_embedding))

    if magnitude_expected == 0 or magnitude_actual == 0:
        return 0.0

    return dot_product / (magnitude_expected * magnitude_actual)

print("\nSemantic similarity:")

for item in golden_dataset:

    output = next(
        x for x in model_outputs
        if x["id"] == item["id"]
    )

    score = semantic_similarity(
        item["expected_answer"],
        output["answer"]
    )

    print(
        item["id"],
        round(score, 2)
    )


def faithfulness(answer, context):

    context_words = set(
        context.lower().split()
    )

    answer_words = set(
        answer.lower().split()
    )

    if not answer_words:
        return 0

    supported_words = answer_words.intersection(
        context_words
    )

    return len(supported_words) / len(answer_words) 

print("\nFaithfulness:")

for item in golden_dataset:

    output = next(
        x for x in model_outputs
        if x["id"] == item["id"]
    )

    score = faithfulness(
        output["answer"],
        output["retrieved_context"]
    )

    print(
        item["id"],
        round(score, 2)
    )


print("\nEvaluation Report")
print("-" * 70)

for item in golden_dataset:

    output = next(
        x for x in model_outputs
        if x["id"] == item["id"]
    )

    semantic_score = semantic_similarity(
        item["expected_answer"],
        output["answer"]
    )

    faithfulness_score = faithfulness(
        output["answer"],
        output["retrieved_context"]
    )

    print(
        f"{item['id']} | "
        f"Semantic: {semantic_score:.2f} | "
        f"Faithfulness: {faithfulness_score:.2f}"
    )