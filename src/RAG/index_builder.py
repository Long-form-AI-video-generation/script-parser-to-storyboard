from pdf_loader import load_script
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


def build_index(pdf_path, persist_dir="./rag_db"):
    # Load pdf
    text = load_script(pdf_path)

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = splitter.split_text(text)

    # Embedd
    hf = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    # Build and save vector store
    Chroma.from_texts(
        texts=splits,
        embedding=hf,
        persist_directory=persist_dir
    )

    print(f" Vector store created and saved in '{persist_dir}'")

if __name__ == "__main__":
    anime_script_path = r"/src/RAG/Anime Scripts/sample.pdf"
    build_index(anime_script_path)
