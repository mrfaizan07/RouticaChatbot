"""Citation formatting and source extraction."""

from app.schemas.chat import CitationSource


class CitationService:
    @staticmethod
    def extract_citations(retrieved_chunks: list[dict]) -> list[CitationSource]:
        """Extracts and deduplicates clean CitationSource objects from retrieved chunks."""
        seen_urls = set()
        citations = []

        for chunk in retrieved_chunks:
            url = chunk.get("source_url", "https://routica.com")
            title = chunk.get("source_title", "Routica Knowledge")
            source_type = chunk.get("source_type", "website")
            score = chunk.get("score")

            content = chunk.get("content", "").strip()
            snippet = content[:150] + "..." if len(content) > 150 else content

            if url not in seen_urls:
                seen_urls.add(url)
                citations.append(
                    CitationSource(
                        title=title,
                        url=url,
                        source_type=source_type,
                        relevance_score=round(score, 3) if score else None,
                        snippet=snippet,
                    )
                )

        return citations

