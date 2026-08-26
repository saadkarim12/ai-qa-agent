"""XLSX document parser using openpyxl.

Spreadsheets are inherently structured — this is where rule-based extraction
shines. Each sheet becomes a table chunk with typed columns. The extraction
engine can directly map columns like "Test Case ID", "Precondition", "Steps"
to the Requirement schema without needing an LLM.
"""

from __future__ import annotations

import logging
from pathlib import Path

import openpyxl

from .base import (
    DocumentFormat,
    IDocumentParser,
    ParsedChunk,
    ParseResult,
    ParseWarning,
    parser_registry,
)

logger = logging.getLogger(__name__)


class XlsxParser(IDocumentParser):
    """XLSX parser — extracts each sheet as a structured table."""

    def supported_formats(self) -> list[DocumentFormat]:
        return [DocumentFormat.XLSX]

    async def parse(self, file_path: Path, content_type: str) -> ParseResult:
        chunks: list[ParsedChunk] = []
        warnings: list[ParseWarning] = []

        try:
            wb = openpyxl.load_workbook(str(file_path), read_only=True, data_only=True)

            for sheet_name in wb.sheetnames:
                try:
                    ws = wb[sheet_name]
                    rows = list(ws.iter_rows(values_only=True))

                    if not rows or len(rows) < 2:
                        warnings.append(
                            ParseWarning(
                                page=None,
                                message=f"Sheet '{sheet_name}' has insufficient data (< 2 rows)",
                            )
                        )
                        continue

                    # First row = headers
                    headers = [
                        str(cell).strip().lower().replace(" ", "_") if cell else ""
                        for cell in rows[0]
                    ]

                    if not any(headers):
                        continue

                    # Build row dicts
                    table_data = []
                    for row_idx, row in enumerate(rows[1:], start=2):
                        row_dict = {}
                        for col_idx, cell in enumerate(row):
                            if col_idx < len(headers) and headers[col_idx]:
                                value = str(cell).strip() if cell is not None else ""
                                row_dict[headers[col_idx]] = value
                        if any(row_dict.values()):
                            table_data.append(row_dict)

                    if table_data:
                        chunks.append(
                            ParsedChunk(
                                content=self._table_to_text(headers, table_data),
                                section_title=sheet_name,
                                chunk_type="table",
                                table_data=table_data,
                                metadata={
                                    "sheet_name": sheet_name,
                                    "row_count": len(table_data),
                                    "columns": [h for h in headers if h],
                                },
                            )
                        )

                except Exception as e:
                    warnings.append(
                        ParseWarning(
                            page=None,
                            message=f"Failed to parse sheet '{sheet_name}': {e}",
                        )
                    )

            wb.close()

        except Exception as e:
            logger.error(f"Failed to open XLSX: {e}")
            warnings.append(
                ParseWarning(
                    page=None,
                    message=f"Failed to open XLSX: {str(e)}",
                    severity="error",
                )
            )

        return ParseResult(
            chunks=chunks,
            total_pages=len(chunks),  # One "page" per sheet
            warnings=warnings,
            metadata={"format": "xlsx", "file": str(file_path.name)},
        )

    def _table_to_text(self, headers: list[str], table_data: list[dict]) -> str:
        """Render as readable text."""
        active_headers = [h for h in headers if h]
        lines = [" | ".join(active_headers)]
        lines.append(" | ".join(["---"] * len(active_headers)))
        for row in table_data:
            lines.append(" | ".join(row.get(h, "") for h in active_headers))
        return "\n".join(lines)


parser_registry.register(XlsxParser())
