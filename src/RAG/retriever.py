from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def query_rag(prompt: str, top_k: int = 3, persist_dir="./rag_db"):

    hf = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vector_store = Chroma(persist_directory=persist_dir, embedding_function=hf)
    results = vector_store.similarity_search(prompt, k=top_k)
    return [r.page_content for r in results]
