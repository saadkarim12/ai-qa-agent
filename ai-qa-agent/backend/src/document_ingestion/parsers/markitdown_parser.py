"""MarkItDown parser wrapper using Microsoft MarkItDown CLI / SDK.

Converts PDF, DOCX, XLSX, HTML, and images to clean Markdown, which is then
chunked and ingested into the Requirement Intelligence pipeline & Memory Store.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from .base import (
    DocumentFormat,
    IDocumentParser,
    ParsedChunk,
    ParseResult,
    ParseWarning,
    parser_registry,
)

logger = logging.getLogger(__name__)


class MarkItDownParser(IDocumentParser):
    """Parser leveraging MarkItDown for universal document-to-markdown conversion."""

    def supported_formats(self) -> list[DocumentFormat]:
        return [
            DocumentFormat.PDF,
            DocumentFormat.DOCX,
            DocumentFormat.XLSX,
            DocumentFormat.HTML,
            DocumentFormat.MARKDOWN,
        ]

    async def parse(self, file_path: Path, content_type: str) -> ParseResult:
        warnings: list[ParseWarning] = []

        try:
            # Execute markitdown via subprocess CLI for robust conversion
            proc = await asyncio.create_subprocess_exec(
                "markitdown",
                str(file_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                err_msg = stderr.decode("utf-8", errors="replace")
                logger.error(f"MarkItDown CLI error on {file_path.name}: {err_msg}")
                warnings.append(
                    ParseWarning(
                        page=None,
                        message=f"MarkItDown conversion warning: {err_msg[:200]}",
                        severity="warning",
                    )
                )

            md_content = stdout.decode("utf-8", errors="replace").strip()
            if not md_content and file_path.exists():
                # Fallback to direct reading if it's already markdown/text
                md_content = file_path.read_text(encoding="utf-8", errors="replace")

        except Exception as e:
            logger.error(f"Failed to run MarkItDown on {file_path.name}: {e}")
            warnings.append(
                ParseWarning(
                    page=None,
                    message=f"MarkItDown execution failed: {str(e)}",
                    severity="error",
                )
            )
            md_content = ""

        # Chunk the generated markdown content by section headers
        chunks = self._chunk_markdown(md_content)

        return ParseResult(
            chunks=chunks,
            total_pages=max(1, len(chunks)),
            warnings=warnings,
            metadata={"format": file_path.suffix.lstrip("."), "parser": "MarkItDown"},
        )

    def _chunk_markdown(self, md_text: str) -> list[ParsedChunk]:
        """Split markdown text into logical chunks by headings."""
        if not md_text.strip():
            return []

        lines = md_text.splitlines()
        chunks: list[ParsedChunk] = []

        current_heading: str | None = None
        current_lines: list[str] = []
        page_num = 1

        for line in lines:
            stripped = line.strip()
            # Detect Markdown headers (#, ##, ###)
            if stripped.startswith("#"):
                if current_lines:
                    chunk_text = "\n".join(current_lines).strip()
                    if chunk_text:
                        chunks.append(
                            ParsedChunk(
                                content=chunk_text,
                                page_number=page_num,
                                section_title=current_heading,
                                chunk_type="markdown",
                            )
                        )
                        page_num += 1
                    current_lines = []

                # Extract header text
                current_heading = stripped.lstrip("#").strip()
                current_lines.append(line)
            else:
                current_lines.append(line)

        # Flush final chunk
        if current_lines:
            chunk_text = "\n".join(current_lines).strip()
            if chunk_text:
                chunks.append(
                    ParsedChunk(
                        content=chunk_text,
                        page_number=page_num,
                        section_title=current_heading,
                        chunk_type="markdown",
                    )
                )

        return chunks


# Register MarkItDown parser globally
parser_registry.register(MarkItDownParser())
