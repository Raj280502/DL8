"""RAG chat service for neuroanatomy QA.

Uses Pinecone for vector search and Groq for fast LLM inference.
"""

from functools import lru_cache
from pathlib import Path
from typing import Dict, List
import os

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from operator import itemgetter
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

# Load environment variables from project root .env if present
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_DEFAULT_INDEX = os.getenv("PINECONE_INDEX_NAME", "neuro-index")
_DEFAULT_NAMESPACE = "neuro"
_EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"
_PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")


def _require_env(keys: List[str]) -> str:
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    joined = ", ".join(keys)
    raise EnvironmentError(f"Missing required environment variable(s): {joined}")


@lru_cache(maxsize=1)
def _embedder() -> HuggingFaceEmbeddings:
    # Keep embeddings normalized for cosine similarity search
    return HuggingFaceEmbeddings(
        model_name=_EMBED_MODEL_NAME,
        encode_kwargs={"normalize_embeddings": True},
    )


@lru_cache(maxsize=8)
def _vector_store(index_name: str = _DEFAULT_INDEX, namespace: str = _DEFAULT_NAMESPACE) -> PineconeVectorStore:
    api_key = _require_env(["PINECONE_API_KEY"])
    environment = _PINECONE_ENVIRONMENT
    if environment:
        pc = Pinecone(api_key=api_key, environment=environment)
    else:
        pc = Pinecone(api_key=api_key)

    # Ensure the index exists so the app does not fail on cold start
    existing = [idx.name for idx in pc.list_indexes()]
    if index_name not in existing:
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    return PineconeVectorStore(
        index_name=index_name,
        embedding=_embedder(),
        namespace=namespace,
    )


@lru_cache(maxsize=1)
def _llm() -> ChatGroq:
    """Get cached Groq LLM instance."""
    try:
        api_key = _require_env(["GROQ_API_KEY"])
        print(f"✅ Found GROQ_API_KEY: {api_key[:10]}...")
        llm = ChatGroq(
            api_key=api_key,
            model="llama-3.1-8b-instant",  # Fast, lightweight, free tier friendly
            temperature=0.3,
            max_tokens=512,
        )
        print("✅ Groq LLM initialized with llama-3.1-8b-instant")
        return llm
    except EnvironmentError as e:
        print(f"❌ Groq API key not configured: {e}")
        raise
    except Exception as e:
        print(f"❌ Error initializing Groq LLM: {type(e).__name__}: {e}")
        raise


@lru_cache(maxsize=1)
def _prompt() -> ChatPromptTemplate:
    template = (
        "Based on the following medical context, answer the question directly and concisely.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Provide a clear, helpful answer:"
    )
    return ChatPromptTemplate.from_template(template)


def _format_docs(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def _format_sources(docs) -> List[str]:
    sources: List[str] = []
    for doc in docs:
        source = doc.metadata.get("source", "")
        page = doc.metadata.get("page")
        page_label = f"p.{page}" if page is not None else None
        label = " - ".join(filter(None, [source, page_label]))
        sources.append(label or "unknown")
    return sources


def answer_question(question: str, index_name: str = _DEFAULT_INDEX, namespace: str = _DEFAULT_NAMESPACE) -> Dict[str, object]:
    if not question or not question.strip():
        raise ValueError("Question must not be empty.")

    try:
        retriever = _vector_store(index_name, namespace).as_retriever(search_kwargs={"k": 4})
        docs = retriever.invoke(question)
        context = _format_docs(docs)

        chain = (
            {
                "context": itemgetter("context"),
                "question": itemgetter("question"),
            }
            | _prompt()
            | _llm()
            | StrOutputParser()
        )

        answer = chain.invoke({"context": context, "question": question.strip()})
        return {
            "answer": answer.strip(),
            "sources": _format_sources(docs),
        }
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__

        print(f"❌ Chat Error ({error_type}): {error_msg}")

        if "Unauthorized" in error_msg or "401" in error_msg or "API key" in error_msg.lower() or "authentication" in error_msg.lower():
            return {
                "answer": f"❌ Groq API Error: {error_msg}\n\n✅ Solution:\n1. Check your Groq API key at https://console.groq.com\n2. Make sure it's not expired\n3. Verify it's in your .env file as: GROQ_API_KEY=\"gsk_...\"\n4. Restart Django server",
                "sources": ["Groq API Configuration Error"],
            }
        else:
            return {
                "answer": f"❌ Chat Error: {error_msg}",
                "sources": ["Error"],
            }
