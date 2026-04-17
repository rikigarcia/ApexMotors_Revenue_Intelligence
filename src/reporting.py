from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from fpdf import FPDF


@dataclass(frozen=True)
class ExecutiveSnapshot:
    generated_at: str
    leads_filtered: int
    vip: int
    hot: int
    nurture: int
    avg_prob_pct: float
    actual_rate_pct: float
    overdue_30: int
    attrition_risk: int
    vip_at_risk: int
    bullets: list[str]


def _pdf_safe(text: str) -> str:
    """
    FPDF (classic) defaults to latin-1 and will throw on unicode punctuation.
    Convert common executive UI glyphs into safe ASCII equivalents.
    """
    replacements = {
        "\u2014": "-",  # em dash
        "\u2013": "-",  # en dash
        "\u2212": "-",  # minus sign
        "\u2022": "*",  # bullet
        "\u00b7": "*",  # middle dot
        "\u2265": ">=",  # ≥
        "\u2264": "<=",  # ≤
        "\u00a0": " ",  # nbsp
        "\u2018": "'",  # left single quote
        "\u2019": "'",  # right single quote
        "\u201c": '"',  # left double quote
        "\u201d": '"',  # right double quote
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Final safety: drop anything outside latin-1
    return text.encode("latin-1", errors="ignore").decode("latin-1")


def build_executive_snapshot_pdf(snapshot: ExecutiveSnapshot) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 9, _pdf_safe("ApexMotors — Revenue Intelligence"), ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, _pdf_safe(f"Executive Snapshot • Generated {snapshot.generated_at}"), ln=True)
    pdf.ln(3)

    # KPI block
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "Key indicators", ln=True)
    pdf.set_font("Helvetica", "", 11)
    lines = [
        f"Leads (filtered): {snapshot.leads_filtered:,}",
        f"VIP / Hot / Nurture: {snapshot.vip:,} / {snapshot.hot:,} / {snapshot.nurture:,}",
        f"Avg predicted purchase probability: {snapshot.avg_prob_pct:.1f}%",
        f"Actual purchase rate: {snapshot.actual_rate_pct:.1f}%",
        f"Overdue follow-ups (≥30 days): {snapshot.overdue_30:,}",
        f"Attrition risk flagged: {snapshot.attrition_risk:,}",
        f"VIP at risk (≥14 days no contact): {snapshot.vip_at_risk:,}",
    ]
    for line in lines:
        pdf.multi_cell(0, 6, _pdf_safe(f"- {line}"))
    pdf.ln(2)

    # Bullets
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "Board-ready summary (3 bullets)", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for b in snapshot.bullets[:3]:
        pdf.multi_cell(0, 6, _pdf_safe(f"* {b}"))
        pdf.ln(1)

    # Footer
    pdf.ln(6)
    pdf.set_text_color(120, 120, 120)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(
        0,
        4.5,
        _pdf_safe(
            "Notes: Predicted probabilities come from the XGBoost champion model when available. "
            "If the artifact cannot be loaded, the system uses a transparent rules-based fallback."
        ),
    )

    # Output (FPDF returns a latin-1 string)
    return pdf.output(dest="S").encode("latin-1", errors="ignore")


def now_iso_local() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")

