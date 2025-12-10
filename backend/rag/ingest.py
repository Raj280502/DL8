"""Ingest the Neuroanatomy PDF into Pinecone for RAG.

Usage:
    export PINECONE_API_KEY=...
    python rag/ingest.py \
        --pdf-path data/neuroanatomy-through-clinical-cases-second-edition-0878936130-9780878936137_compress.pdf \
        --index neuro-index \
        --namespace neuro

Notes:
- Requires dependencies from backend/requirements.txt (langchain, pinecone, sentence-transformers, pypdf).
- Uses BAAI/bge-small-en-v1.5 embeddings (384-dim). Adjust model_name if needed.
"""

import argparse
import os
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec


def ingest(pdf_path: str, index_name: str, namespace: str):
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found at {pdf_path}")

    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise EnvironmentError("PINECONE_API_KEY not set")

    print(f"Loading PDF: {pdf_path}")
    loader = PyPDFLoader(str(pdf_path))
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", ",", " "],
    )
    print("Splitting document into chunks ...")
    splits = splitter.split_documents(docs)
    print(f"Total chunks: {len(splits)}")

    embed_model_name = "BAAI/bge-small-en-v1.5"  # 384-dim
    print(f"Loading embeddings: {embed_model_name}")
    embedder = HuggingFaceBgeEmbeddings(
        model_name=embed_model_name,
        normalize_embeddings=True,
    )

    print(f"Connecting to Pinecone index: {index_name}")
    pc = Pinecone(api_key=api_key)
    # Create index if missing
    if index_name not in [idx.name for idx in pc.list_indexes()]:
        print("Index not found. Creating ...")
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    index = pc.Index(index_name)

    print(f"Upserting {len(splits)} chunks into Pinecone (namespace='{namespace}') ...")
    PineconeVectorStore.from_documents(
        documents=splits,
        embedding=embedder,
        index_name=index_name,
        namespace=namespace,
    )
    print("✅ Ingestion complete.")


def parse_args():
    parser = argparse.ArgumentParser(description="Ingest Neuroanatomy PDF into Pinecone store")
    parser.add_argument(
        "--pdf-path",
        default="data/neuroanatomy-through-clinical-cases-second-edition-0878936130-9780878936137_compress.pdf",
        help="Path to the PDF to ingest",
    )
    parser.add_argument(
        "--index",
        default="neuro-index",
        help="Pinecone index name",
    )
    parser.add_argument(
        "--namespace",
        default="neuro",
        help="Pinecone namespace to use",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    ingest(args.pdf_path, args.index, args.namespace)
