"""RAG chat service for neuroanatomy QA.

Uses Pinecone for vector search over the ingested PDF and a Hugging Face
Llama 3.2 8B Instruct endpoint for generation.
"""

from functools import lru_cache
from pathlib import Path
from typing import Dict, List
import os

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.llms import LLM
from operator import itemgetter
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from huggingface_hub import InferenceClient

# Load environment variables from project root .env if present
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_DEFAULT_INDEX = "neuro-index"
_DEFAULT_NAMESPACE = "neuro"
_EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"
# Use a model available on HF serverless inference
_LLM_REPO = "HuggingFaceH4/zephyr-7b-beta"


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


class _HFChatLLM(LLM):
    """LLM wrapper using HuggingFace InferenceClient chat_completion API."""

    model: str = _LLM_REPO
    token: str = ""
    max_new_tokens: int = 256
    temperature: float = 0.1

    @property
    def _llm_type(self) -> str:
        return "hf_chat"

    def _call(self, prompt: str, stop=None, run_manager=None, **kwargs) -> str:
        client = InferenceClient(token=self.token)
        # Use chat_completion with a system message for better control
        response = client.chat_completion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful medical assistant. Give direct, concise answers. Do not generate follow-up questions or continue the conversation. Just answer the question asked."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_new_tokens,
            temperature=self.temperature,
            stop=["Question:", "Human:", "\n\n\n"],
        )
        answer = response.choices[0].message.content
        # Clean up any trailing artifacts
        for marker in ["Question:", "Human:", "[/INST]", "[/ASS]"]:
            if marker in answer:
                answer = answer.split(marker)[0]
        return answer.strip()


@lru_cache(maxsize=1)
def _llm() -> _HFChatLLM:
    token = _require_env([
        "HUGGINGFACEHUB_API_TOKEN",
        "HF_TOKEN",
        "HUGGINGFACE_API_KEY",
    ])
    return _HFChatLLM(
        model=_LLM_REPO,
        token=token,
        temperature=0.3,
        max_new_tokens=512,
    )


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
