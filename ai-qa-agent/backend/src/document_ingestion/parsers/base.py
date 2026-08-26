"""Document parser interface and registry.

Every document format implements IDocumentParser. Adding a new format means
writing a new class and registering it — the pipeline never changes (HLD §8.4).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Protocol


class DocumentFormat(str, Enum):
    """Supported document formats for ingestion."""

    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    MARKDOWN = "markdown"
    HTML = "html"
    CSV = "csv"
    UNKNOWN = "unknown"


@dataclass
class ParsedChunk:
    """A single extracted chunk from a document.

    Chunks are the unit of processing — each one goes through the
    requirement extraction pipeline independently. This enables
    partial failure: one bad page doesn't kill the whole document.
    """

    content: str
    page_number: int | None = None
    section_title: str | None = None
    chunk_type: str = "text"  # text | table | list | heading
    table_data: list[dict] | None = None  # Structured table rows
    metadata: dict = field(default_factory=dict)


@dataclass
class ParseWarning:
    """A non-fatal issue encountered during parsing."""

    page: int | None
    message: str
    severity: str = "warning"  # warning | error


@dataclass
class ParseResult:
    """Output of a document parser. Contains all extracted chunks + any warnings.

    The pipeline is staged so that failure is partial and visible:
    an unparseable page degrades to a warning, never to a silent gap (HLD §4.1).
    """

    chunks: list[ParsedChunk]
    total_pages: int
    warnings: list[ParseWarning] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)  # Document-level metadata


class IDocumentParser(ABC):
    """Interface for document format parsers (HLD Table 30: IDocumentParser).

    Implementations: PDF, DOCX, XLSX, HTML, Markdown, image+OCR.
    Adding a new format = implementing this interface + registering it.
    """

    @abstractmethod
    def supported_formats(self) -> list[DocumentFormat]:
        """Which formats this parser handles."""
        ...

    @abstractmethod
    async def parse(self, file_path: Path, content_type: str) -> ParseResult:
        """Parse a document and return structured chunks.

        Must handle failures gracefully — return warnings for unparseable
        sections rather than raising exceptions.
        """
        ...


class ParserRegistry:
    """Registry of document parsers by format.

    The pipeline asks the registry for the right parser based on
    format detection results. New parsers register themselves here.
    """

    def __init__(self) -> None:
        self._parsers: dict[DocumentFormat, IDocumentParser] = {}

    def register(self, parser: IDocumentParser) -> None:
        for fmt in parser.supported_formats():
            self._parsers[fmt] = parser

    def get_parser(self, fmt: DocumentFormat) -> IDocumentParser | None:
        return self._parsers.get(fmt)

    def supported_formats(self) -> list[DocumentFormat]:
        return list(self._parsers.keys())


# Global registry — parsers register at import time
parser_registry = ParserRegistry()
