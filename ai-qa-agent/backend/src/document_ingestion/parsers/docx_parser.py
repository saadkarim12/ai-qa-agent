"""DOCX document parser using python-docx.

Extracts text, headings, tables, and list items with structural awareness.
"""

from __future__ import annotations

import logging
from pathlib import Path

from docx import Document as DocxDocument
from docx.table import Table as DocxTable

from .base import (
    DocumentFormat,
    IDocumentParser,
    ParsedChunk,
    ParseResult,
    ParseWarning,
    parser_registry,
)

logger = logging.getLogger(__name__)


class DocxParser(IDocumentParser):
    """DOCX parser using python-docx for structured content extraction."""

    def supported_formats(self) -> list[DocumentFormat]:
        return [DocumentFormat.DOCX]

    async def parse(self, file_path: Path, content_type: str) -> ParseResult:
        chunks: list[ParsedChunk] = []
        warnings: list[ParseWarning] = []

        try:
            doc = DocxDocument(str(file_path))

            # --- Extract tables ---
            for table_idx, table in enumerate(doc.tables):
                try:
                    parsed = self._parse_table(table)
                    if parsed:
                        chunks.append(
                            ParsedChunk(
                                content=self._table_to_text(parsed),
                                chunk_type="table",
                                table_data=parsed,
                                metadata={"table_index": table_idx},
                            )
                        )
                except Exception as e:
                    warnings.append(
                        ParseWarning(
                            page=None,
                            message=f"Failed to parse table {table_idx}: {e}",
                        )
                    )

            # --- Extract paragraphs grouped by heading ---
            current_section: str | None = None
            current_content: list[str] = []

            for para in doc.paragraphs:
                try:
                    style_name = para.style.name if para.style else ""
                    text = para.text.strip()

                    if not text:
                        continue

                    # Detect headings → start new section
                    if style_name and "heading" in style_name.lower():
                        # Flush previous section
                        if current_content:
                            chunks.append(
                                ParsedChunk(
                                    content="\n".join(current_content),
                                    section_title=current_section,
                                    chunk_type="text",
                                )
                            )
                            current_content = []
                        current_section = text

                    elif style_name and "list" in style_name.lower():
                        current_content.append(f"• {text}")

                    else:
                        current_content.append(text)

                except Exception as e:
                    warnings.append(
                        ParseWarning(
                            page=None,
                            message=f"Failed to parse paragraph: {e}",
                        )
                    )

            # Flush remaining content
            if current_content:
                chunks.append(
                    ParsedChunk(
                        content="\n".join(current_content),
                        section_title=current_section,
                        chunk_type="text",
                    )
                )

        except Exception as e:
            logger.error(f"Failed to open DOCX: {e}")
            warnings.append(
                ParseWarning(
                    page=None,
                    message=f"Failed to open DOCX: {str(e)}",
                    severity="error",
                )
            )

        # DOCX doesn't have real "pages" — estimate from paragraph count
        estimated_pages = max(1, len(chunks))

        return ParseResult(
            chunks=chunks,
            total_pages=estimated_pages,
            warnings=warnings,
            metadata={"format": "docx", "file": str(file_path.name)},
        )

    def _parse_table(self, table: DocxTable) -> list[dict] | None:
        """Convert a DOCX table into list of dicts using first row as headers."""
        rows = table.rows
        if len(rows) < 2:
            return None

        headers = [
            (cell.text or "").strip().lower().replace(" ", "_")
            for cell in rows[0].cells
        ]

        if not any(headers):
            return None

        result = []
        for row in rows[1:]:
            row_dict = {}
            for i, cell in enumerate(row.cells):
                if i < len(headers) and headers[i]:
                    row_dict[headers[i]] = (cell.text or "").strip()
            if any(row_dict.values()):
                result.append(row_dict)

        return result if result else None

    def _table_to_text(self, table_data: list[dict]) -> str:
        """Render table as readable text."""
        if not table_data:
            return ""
        headers = list(table_data[0].keys())
        lines = [" | ".join(headers)]
        lines.append(" | ".join(["---"] * len(headers)))
        for row in table_data:
            lines.append(" | ".join(row.get(h, "") for h in headers))
        return "\n".join(lines)


parser_registry.register(DocxParser())
