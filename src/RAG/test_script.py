from retriever import query_rag

if __name__ == "__main__":
    prompt = "What is the setting of the story?"
    results = query_rag(prompt, top_k=3)

    print("Top results from RAG:")
    for i, r in enumerate(results, 1):
        print(f"\n--- Result {i} ---\n{r}\n")
