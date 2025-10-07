"""Status Pack export utilities."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from app.backend.models import DashboardPayload, StatusPackResult


def _rag_state(spi: float | None, cpi: float | None) -> str:
    if spi is None or cpi is None:
        return "Watch"
    if spi >= 1.0 and cpi >= 1.0:
        return "On Track"
    if spi >= 0.95 and cpi >= 0.95:
        return "Watch"
    return "At Risk"


def _build_markdown(payload: DashboardPayload) -> str:
    evm = payload.evm
    rag = _rag_state(evm.spi, evm.cpi)
    lines = [
        f"# ASR Copilot Status Pack ({payload.meta.last_updated.date()})",
        "",
        f"**Overall RAG:** {rag}",
        "",
        "## Executive Summary",
        payload.narrative,
        "",
        "## Earned Value Metrics",
        "| Metric | Value |",
        "| ------ | ----- |",
        f"| PV | {evm.pv:.2f} |",
        f"| EV | {evm.ev:.2f} |",
        f"| AC | {evm.ac:.2f} |",
        f"| SV | {evm.sv:.2f} |",
        f"| CV | {evm.cv:.2f} |",
        f"| SPI | {evm.spi if evm.spi is not None else 'n/a'} |",
        f"| CPI | {evm.cpi if evm.cpi is not None else 'n/a'} |",
        f"| EAC | {evm.eac if evm.eac is not None else 'n/a'} |",
        f"| ETC | {evm.etc if evm.etc is not None else 'n/a'} |",
        "",
        "## Top Risks",
    ]
    if payload.risks.top_risks:
        lines.append("| ID | Risk | Severity | Due | Owner | Mitigation |")
        lines.append("| -- | ---- | -------- | --- | ----- | ---------- |")
        for risk in payload.risks.top_risks:
            lines.append(
                f"| {risk.id} | {risk.summary} | {risk.severity:.2f} ({risk.status}) | "
                f"{risk.due_date} | {risk.owner} | {risk.mitigation or 'TBD'} |"
            )
    else:
        lines.append("_No active risks._")

    lines.extend(
        [
            "",
            "## What Changed Since Last Snapshot",
        ]
    )

    if payload.changes.has_changes:
        for change in payload.changes.items:
            lines.append(
                f"- **{change.entity_type.title()} {change.change_type}** – "
                f"{change.title} ({change.timestamp.strftime('%Y-%m-%d %H:%M')})"
            )
            lines.append(f"  - {change.detail}")
    else:
        lines.append("No changes detected.")

    lines.extend(
        [
            "",
            "## ROI Snapshot",
            f"- Annual savings estimate: ${payload.roi.annual_savings:,.2f}",
            f"- Monthly savings estimate: ${payload.roi.monthly_savings:,.2f}",
            f"- Annual hours reclaimed: {payload.roi.total_hours_saved:,.1f}",
        ]
    )

    return "\n".join(lines)


def _evm_chart(payload: DashboardPayload, output_path: Path) -> None:
    evm = payload.evm
    labels = ["PV", "EV", "AC"]
    values = [evm.pv, evm.ev, evm.ac]
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, values, color=["#1245A6", "#2E8B57", "#C73535"])
    ax.set_title("Earned Value Snapshot")
    ax.set_ylabel("Hours (proxy)")
    ax.bar_label(bars, fmt="%.0f")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _risk_heatmap_chart(payload: DashboardPayload, output_path: Path) -> None:
    risks = payload.risks.heatmap
    fig, ax = plt.subplots(figsize=(6, 4))
    x = [risk.probability for risk in risks]
    y = [risk.impact for risk in risks]
    sizes = [(5 - risk.summary.count(" ")) * 20 + 40 for risk in risks]  # heuristic sizing
    scatter = ax.scatter(x, y, s=sizes, c=[risk.severity for risk in risks], cmap="Reds")
    ax.set_xlabel("Probability")
    ax.set_ylabel("Impact (1-5)")
    ax.set_title("Risk Heatmap")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 5.5)
    fig.colorbar(scatter, ax=ax, label="Severity")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def generate_status_pack(
    payload: DashboardPayload,
    out_dir: Path,
    include_markdown: bool = True,
    include_png: bool = True,
) -> StatusPackResult:
    """Create Markdown + PNG assets summarizing program status."""
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    markdown_path: Optional[str] = None
    chart_paths: List[str] = []

    if include_markdown:
        md_content = _build_markdown(payload)
        md_file = out_dir / f"status_pack_{timestamp}.md"
        md_file.write_text(md_content, encoding="utf-8")
        markdown_path = str(md_file)

    if include_png:
        evm_chart_path = out_dir / f"status_pack_{timestamp}_evm.png"
        risk_chart_path = out_dir / f"status_pack_{timestamp}_risk_heatmap.png"
        _evm_chart(payload, evm_chart_path)
        _risk_heatmap_chart(payload, risk_chart_path)
        chart_paths.extend([str(evm_chart_path), str(risk_chart_path)])

    return StatusPackResult(
        markdown_path=markdown_path,
        chart_paths=chart_paths,
        posted_to_slack=False,
        dataset_hash=payload.meta.dataset_hash,
    )
