"""Deterministic narrative generator for executive summary."""

from __future__ import annotations

from typing import List

from app.backend.models import ChangesSummary, EvmMetrics, RiskSummary


def _rag_from_spi_cpi(spi: float | None, cpi: float | None) -> str:
    if spi is None or cpi is None:
        return "Watch"
    if spi >= 1.0 and cpi >= 1.0:
        return "On Track"
    if spi >= 0.95 and cpi >= 0.95:
        return "Watch"
    return "At Risk"


def build_narrative(
    evm: EvmMetrics,
    risks: RiskSummary,
    changes: ChangesSummary,
) -> str:
    """Compose a concise exec-ready narrative."""
    rag_state = _rag_from_spi_cpi(evm.spi, evm.cpi)
    lines: List[str] = []
    lines.append(
        f"Status: {rag_state}. CPI {evm.cpi or 'n/a'} / SPI {evm.spi or 'n/a'} (baseline {evm.baseline_date})."
    )
    if risks.top_risks:
        top = risks.top_risks[0]
        lines.append(
            f"Top risk: {top.summary} (severity {top.severity}, due {top.due_date}). Mitigation: {top.mitigation or 'Pending assignment.'}"
        )
    else:
        lines.append("No active risks logged in the register.")

    if changes.has_changes and changes.items:
        latest = changes.items[0]
        lines.append(
            f"Latest change: {latest.entity_type.title()} {latest.change_type} – {latest.title}."
        )
    else:
        lines.append("No changes detected since previous snapshot.")

    return " ".join(lines)
