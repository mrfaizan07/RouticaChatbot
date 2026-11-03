"""Tests for RAG pipeline: groundedness, citations, comparisons, and missing facts handling."""

import asyncio
from unittest.mock import AsyncMock
import pytest
from app.services.rag_service import RAGService


def test_rag_answers_with_grounded_context():
    async def _run():
        mock_retrieval = AsyncMock()
        mock_retrieval.retrieve_context.return_value = [
            {
                "source_title": "Explorer II",
                "source_url": "https://routica.com/explorer-ii",
                "source_type": "website",
                "score": 0.95,
                "content": "Routica Explorer II is equipped with 5G Sub-6GHz connectivity, dual SIM slots, and Wi-Fi 6 for marine and RV applications.",
            }
        ]

        mock_router = AsyncMock()
        mock_router.execute_with_fallback.return_value = {
            "content": "Explorer II supports high-speed 5G Sub-6GHz connectivity and Wi-Fi 6, specifically designed for marine yachts and RVs.",
            "provider": "gemini",
            "model": "gemini/gemini-1.5-flash",
        }

        rag_service = RAGService(retrieval_service=mock_retrieval, provider_router=mock_router)
        result = await rag_service.answer_question("Does Explorer II support 5G?")

        assert "5G" in result["answer"]
        assert len(result["sources"]) == 1
        assert result["sources"][0]["url"] == "https://routica.com/explorer-ii"
        assert result["provider"] == "gemini"

    asyncio.run(_run())


def test_rag_handles_no_context_gracefully():
    async def _run():
        mock_retrieval = AsyncMock()
        mock_retrieval.retrieve_context.return_value = []

        mock_router = AsyncMock()
        mock_router.execute_with_fallback.return_value = {
            "content": "I could not find verified information in Routica documentation regarding this topic.",
            "provider": "gemini",
            "model": "gemini/gemini-1.5-flash",
        }

        rag_service = RAGService(retrieval_service=mock_retrieval, provider_router=mock_router)
        result = await rag_service.answer_question("What is the secret roadmap for 2030?")

        assert len(result["sources"]) == 0
        assert "not find verified" in result["answer"]

    asyncio.run(_run())


def test_rag_handles_product_comparison():
    async def _run():
        mock_retrieval = AsyncMock()
        mock_retrieval.retrieve_context.return_value = [
            {
                "source_title": "Explorer I",
                "source_url": "https://routica.com/explorer-i",
                "source_type": "website",
                "score": 0.91,
                "content": "Explorer I features 4G LTE Cat 12 with single SIM slot, suitable for standard RVs.",
            },
            {
                "source_title": "Explorer II",
                "source_url": "https://routica.com/explorer-ii",
                "source_type": "website",
                "score": 0.93,
                "content": "Explorer II features 5G Sub-6GHz with dual SIM failover and Wi-Fi 6, engineered for luxury yachts and remote expeditions.",
            },
        ]

        mock_router = AsyncMock()
        mock_router.execute_with_fallback.return_value = {
            "content": "Comparison:\n- Explorer I: 4G LTE Cat 12 with single SIM.\n- Explorer II: 5G Sub-6GHz with dual SIM and Wi-Fi 6.",
            "provider": "gemini",
            "model": "gemini/gemini-1.5-flash",
        }

        rag_service = RAGService(retrieval_service=mock_retrieval, provider_router=mock_router)
        result = await rag_service.answer_question("Compare Explorer I and Explorer II")

        assert "Explorer I" in result["answer"]
        assert "Explorer II" in result["answer"]
        assert len(result["sources"]) == 2

    asyncio.run(_run())


def test_rag_prepare_stream_context():
    async def _run():
        mock_retrieval = AsyncMock()
        mock_retrieval.retrieve_context.return_value = [
            {
                "source_title": "Routica Support",
                "source_url": "https://routica.com/support",
                "source_type": "website",
                "score": 0.88,
                "content": "Default IP for Routica routers is 192.168.8.1.",
            }
        ]
        mock_router = AsyncMock()

        rag_service = RAGService(retrieval_service=mock_retrieval, provider_router=mock_router)
        messages, citations = await rag_service.prepare_stream_context("What is the default router IP?")

        assert len(citations) == 1
        assert citations[0]["url"] == "https://routica.com/support"
        assert len(messages) >= 2
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        assert "192.168.8.1" in messages[-1]["content"]

    asyncio.run(_run())
