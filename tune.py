import json

from langchain_chroma import Chroma
from langchain_community.embeddings import JinaEmbeddings

import config
from ingest import load_documents, split_documents

# Settings to try
CHUNK_SIZES = [300, 500, 800, 1000]
CHUNK_OVERLAPS = [0, 100, 200]
K_VALUES = [2, 3, 4, 6]


def normalize(text):
    """Lowercase and collapse whitespace so line breaks don't break matching."""
    return " ".join(text.lower().split())


def main():
    # 1. Load the questions that the documents can answer
    with open("eval_set.json", encoding="utf-8") as file:
        eval_set = json.load(file)

    questions = []
    for item in eval_set:
        if item["expected_text"] is not None:
            questions.append(item)

    # 2. Load documents and check every expected answer really exists in them
    documents = load_documents()
    all_text = normalize(" ".join(doc.page_content for doc in documents))

    for item in questions:
        if normalize(item["expected_text"]) not in all_text:
            raise SystemExit(f"Expected text not found in the PDFs: {item['expected_text']!r}")

    # 3. Embed the questions once and reuse them for every setting
    embeddings = JinaEmbeddings(model_name=config.EMBEDDING_MODEL)
    question_texts = [item["question"] for item in questions]
    question_vectors = embeddings.embed_documents(question_texts)

    # 4. Try every combination of settings
    results = []

    for chunk_size in CHUNK_SIZES:
        for chunk_overlap in CHUNK_OVERLAPS:
            if chunk_overlap >= chunk_size:
                continue

            chunks = split_documents(documents, chunk_size, chunk_overlap)

            # No persist_directory → kept in memory, the real chroma_db is untouched
            test_store = Chroma(
                collection_name=f"tune_{chunk_size}_{chunk_overlap}",
                embedding_function=embeddings,
            )
            test_store.add_documents(chunks)

            for k in K_VALUES:
                hits = 0
                total_context_chars = 0

                for item, vector in zip(questions, question_vectors):
                    retrieved = test_store.similarity_search_by_vector(vector, k=k)
                    retrieved_text = normalize(" ".join(doc.page_content for doc in retrieved))

                    if normalize(item["expected_text"]) in retrieved_text:
                        hits += 1

                    total_context_chars += sum(len(doc.page_content) for doc in retrieved)

                results.append({
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                    "k": k,
                    "chunks": len(chunks),
                    "hit_rate": hits / len(questions),
                    "avg_context_chars": total_context_chars // len(questions),
                })

            print(f"Tested chunk_size={chunk_size}, chunk_overlap={chunk_overlap} ({len(chunks)} chunks)")

    # 5. Best = finds the answer most often; ties go to the smallest context sent to the LLM
    results.sort(key=lambda r: (-r["hit_rate"], r["avg_context_chars"]))

    print()
    print(f"Evaluated {len(questions)} questions")
    print()
    print(f"{'chunk_size':>10} {'overlap':>8} {'k':>3} {'chunks':>7} {'hit rate':>9} {'avg context':>12}")

    for r in results[:10]:
        print(
            f"{r['chunk_size']:>10} {r['chunk_overlap']:>8} {r['k']:>3} {r['chunks']:>7} "
            f"{r['hit_rate']:>9.0%} {r['avg_context_chars']:>12}"
        )

    for r in results:
        if (r["chunk_size"], r["chunk_overlap"], r["k"]) == (config.CHUNK_SIZE, config.CHUNK_OVERLAP, config.TOP_K):
            print()
            print(
                f"Current config: chunk_size={r['chunk_size']}, overlap={r['chunk_overlap']}, k={r['k']} "
                f"→ hit rate {r['hit_rate']:.0%}, avg context {r['avg_context_chars']} chars"
            )

    best = results[0]
    print(
        f"Best:           chunk_size={best['chunk_size']}, overlap={best['chunk_overlap']}, k={best['k']} "
        f"→ hit rate {best['hit_rate']:.0%}, avg context {best['avg_context_chars']} chars"
    )


if __name__ == "__main__":
    main()
