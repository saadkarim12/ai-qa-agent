"""PDF document parser using pdfplumber.

Extracts text and tables from PDF documents with per-page granularity.
Failures on individual pages produce warnings, not exceptions.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pdfplumber

from .base import (
    DocumentFormat,
    IDocumentParser,
    ParsedChunk,
    ParseResult,
    ParseWarning,
    parser_registry,
)

logger = logging.getLogger(__name__)


class PdfParser(IDocumentParser):
    """PDF parser using pdfplumber for text and table extraction."""

    def supported_formats(self) -> list[DocumentFormat]:
        return [DocumentFormat.PDF]

    async def parse(self, file_path: Path, content_type: str) -> ParseResult:
        chunks: list[ParsedChunk] = []
        warnings: list[ParseWarning] = []
        total_pages = 0

        try:
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        # --- Extract tables first (structured data) ---
                        tables = page.extract_tables()
                        if tables:
                            for table_idx, table in enumerate(tables):
                                parsed_table = self._parse_table(table)
                                if parsed_table:
                                    chunks.append(
                                        ParsedChunk(
                                            content=self._table_to_text(parsed_table),
                                            page_number=page_num,
                                            chunk_type="table",
                                            table_data=parsed_table,
                                            metadata={"table_index": table_idx},
                                        )
                                    )

                        # --- Extract text (excluding table regions) ---
                        text = page.extract_text() or ""
                        text = text.strip()

                        if text:
                            # Split by apparent section headings (lines in ALL CAPS or
                            # lines that start with a number followed by a period)
                            sections = self._split_into_sections(text)
                            for section_title, section_text in sections:
                                if section_text.strip():
                                    chunks.append(
                                        ParsedChunk(
                                            content=section_text.strip(),
                                            page_number=page_num,
                                            section_title=section_title,
                                            chunk_type="text",
                                        )
                                    )

                    except Exception as e:
                        # Per-page failure → warning, not crash (HLD §4.1)
                        logger.warning(f"Failed to parse page {page_num}: {e}")
                        warnings.append(
                            ParseWarning(
                                page=page_num,
                                message=f"Could not extract content: {str(e)}",
                                severity="warning",
                            )
                        )

        except Exception as e:
            logger.error(f"Failed to open PDF: {e}")
            warnings.append(
                ParseWarning(
                    page=None,
                    message=f"Failed to open PDF: {str(e)}",
                    severity="error",
                )
            )

        return ParseResult(
            chunks=chunks,
            total_pages=total_pages,
            warnings=warnings,
            metadata={"format": "pdf", "file": str(file_path.name)},
        )

    def _parse_table(self, raw_table: list[list]) -> list[dict] | None:
        """Convert a raw table (list of lists) into a list of dicts using the first row as headers."""
        if not raw_table or len(raw_table) < 2:
            return None

        headers = [
            (cell or "").strip().lower().replace(" ", "_")
            for cell in raw_table[0]
        ]

        if not any(headers):
            return None

        rows = []
        for row in raw_table[1:]:
            row_dict = {}
            for i, cell in enumerate(row):
                if i < len(headers) and headers[i]:
                    row_dict[headers[i]] = (cell or "").strip()
            if any(row_dict.values()):
                rows.append(row_dict)

        return rows if rows else None

    def _table_to_text(self, table_data: list[dict]) -> str:
        """Render a table as readable text for LLM processing."""
        if not table_data:
            return ""
        headers = list(table_data[0].keys())
        lines = [" | ".join(headers)]
        lines.append(" | ".join(["---"] * len(headers)))
        for row in table_data:
            lines.append(" | ".join(row.get(h, "") for h in headers))
        return "\n".join(lines)

    def _split_into_sections(self, text: str) -> list[tuple[str | None, str]]:
        """Split text into sections based on heading patterns.

        Returns list of (section_title, section_content) tuples.
        """
        import re

        # Pattern: numbered sections like "4.1 Layer Name" or "10. Requirements"
        heading_pattern = re.compile(
            r"^(\d+\.(?:\d+\.?)?\s+.+)$", re.MULTILINE
        )

        parts = heading_pattern.split(text)

        if len(parts) <= 1:
            # No headings found — return as single chunk
            return [(None, text)]

        sections: list[tuple[str | None, str]] = []

        # First part (before any heading)
        if parts[0].strip():
            sections.append((None, parts[0]))

        # Paired heading + content
        for i in range(1, len(parts), 2):
            title = parts[i].strip() if i < len(parts) else None
            content = parts[i + 1] if i + 1 < len(parts) else ""
            sections.append((title, content))

        return sections


# Register with the global registry
parser_registry.register(PdfParser())
