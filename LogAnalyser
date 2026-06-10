from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import re

# =====================================
# STEP 1 - Parse Log File
# =====================================

parsed_logs = []

with open(
    r"C:\Users\vinod\Desktop\TestLogFile.log",
    "r",
    encoding="utf-8"
) as f:

    for line in f:

        line = line.strip()

        match = re.match(
            r'^(\d{2}:\d{2}:\d{2}\.\d+)\s+(\w+)\s+({.*})$',
            line
        )

        if not match:
            continue

        try:

            payload = json.loads(match.group(3))

            parsed_logs.append({
                "message": payload.get("message", ""),
                "timestamp": payload.get("timeStamp", ""),
                "level": payload.get("level", "")
            })

        except Exception:
            pass

# =====================================
# STEP 2 - Extract Transactions
# =====================================

success_transactions = []
failed_transactions = []

for log in parsed_logs:

    msg = str(log["message"])

    success_match = re.search(
        r'Transaction:\s*(\d+)\s*success',
        msg,
        re.IGNORECASE
    )

    failed_match = re.search(
        r'Transaction:\s*(\d+)\s*failed',
        msg,
        re.IGNORECASE
    )

    if success_match:
        success_transactions.append(
            int(success_match.group(1))
        )

    if failed_match:
        failed_transactions.append(
            int(failed_match.group(1))
        )

# =====================================
# STEP 3 - Build Contexts
# =====================================

contexts = []

for txn in success_transactions:

    contexts.append(
        f"Transaction {txn} completed successfully."
    )

for txn in failed_transactions:

    contexts.append(
        f"Transaction {txn} failed."
    )

contexts.append(
    f"Total successful transactions are {len(success_transactions)}."
)

contexts.append(
    f"Total failed transactions are {len(failed_transactions)}."
)

contexts.append(
    f"Total transactions processed are {len(success_transactions) + len(failed_transactions)}."
)

# =====================================
# STEP 4 - Generate Embeddings
# =====================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

embeddings = model.encode(contexts)

# =====================================
# STEP 5 - Create Vector Store
# =====================================

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

vectors = np.array(
    embeddings,
    dtype=np.float32
)

index.add(vectors)

metadata = {
    i: context
    for i, context in enumerate(contexts)
}

# =====================================
# STEP 6 - Statistics Store
# =====================================

stats = {
    "total_transactions":
        len(success_transactions)
        + len(failed_transactions),

    "successful_transactions":
        len(success_transactions),

    "failed_transactions":
        len(failed_transactions),

    "failed_ids":
        failed_transactions,

    "success_ids":
        success_transactions
}

# =====================================
# STEP 7 - Question Answering
# =====================================

def answer_question(question):

    query = question.lower()

    # -------------------------
    # COUNT FAILED
    # -------------------------

    if (
        any(x in query for x in
            ["how many", "count", "number", "total"])
        and
        any(x in query for x in
            ["failed", "failure", "unsuccessful"])
    ):

        return (
            f"Total failed transactions: "
            f"{stats['failed_transactions']}"
        )

    # -------------------------
    # COUNT SUCCESS
    # -------------------------

    if (
        any(x in query for x in
            ["how many", "count", "number", "total"])
        and
        any(x in query for x in
            ["success", "successful"])
    ):

        return (
            f"Total successful transactions: "
            f"{stats['successful_transactions']}"
        )

    # -------------------------
    # LIST FAILED
    # -------------------------

    if (
        "which" in query
        or "show" in query
        or "list" in query
    ) and "failed" in query:

        return (
            "Failed transactions: "
            + ", ".join(
                map(str, stats["failed_ids"])
            )
        )

    # -------------------------
    # SUMMARY
    # -------------------------

    if (
        "summary" in query
        or "summarize" in query
        or "overview" in query
    ):

        return f"""
Execution Summary

Total Transactions:
{stats['total_transactions']}

Successful:
{stats['successful_transactions']}

Failed:
{stats['failed_transactions']}
"""

    # -------------------------
    # VECTOR SEARCH
    # -------------------------

    query_vector = model.encode(
        [question]
    )

    query_vector = np.array(
        query_vector,
        dtype=np.float32
    )

    k = min(5, index.ntotal)

    D, I = index.search(
        query_vector,
        k
    )

    results = []

    for idx in I[0]:

        if idx != -1:

            results.append(
                metadata[idx]
            )

    return "\n".join(results)

# =====================================
# STEP 8 - Chat Loop
# =====================================

print("\nLog Analytics Agent Started")
print("Type 'exit' to quit\n")

while True:

    question = input(
        "\nAsk Question: "
    )

    if question.lower() == "exit":
        break

    answer = answer_question(
        question
    )

    print("\nAnswer:")
    print(answer)