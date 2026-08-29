"""
report.py
---------
Turns query results into a formatted PDF. This is pure rendering logic --
it has no idea it's running inside a background job. That separation is
what makes it testable on its own (see tests/test_report.py).
"""

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)

from app import queries


def build_sales_report(start_date: str, end_date: str, output_path: Path) -> Path:
    """
    Query the DB, render a PDF sales report to output_path, and
    return the path. This is the single function the job worker calls.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    totals = queries.overall_totals(start_date, end_date)
    by_region = queries.sales_summary_by_region(start_date, end_date)
    top = queries.top_products(start_date, end_date, limit=10)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        title="Sales Report",
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    story = []

    story.append(Paragraph("Sales Report", styles["Title"]))
    story.append(Paragraph(f"Period: {start_date} to {end_date}", styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # --- Headline numbers ---
    revenue = totals["total_revenue"] or 0
    headline_data = [
        ["Total Revenue", "Total Orders", "Unique Customers"],
        [
            f"${revenue:,.2f}",
            str(totals["total_orders"] or 0),
            str(totals["unique_customers"] or 0),
        ],
    ]
    headline_table = Table(headline_data, colWidths=[2.2 * inch] * 3)
    headline_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d3748")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 1), (-1, 1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    story.append(headline_table)
    story.append(Spacer(1, 0.4 * inch))

    # --- Revenue by region ---
    story.append(Paragraph("Revenue by Region", styles["Heading2"]))
    region_data = [["Region", "Orders", "Revenue"]]
    for row in by_region:
        region_data.append(
            [row["region"], str(row["order_count"]), f"${row['revenue']:,.2f}"]
        )
    region_table = Table(region_data, colWidths=[2.5 * inch, 1.5 * inch, 2.5 * inch])
    region_table.setStyle(_table_style())
    story.append(region_table)
    story.append(Spacer(1, 0.4 * inch))

    # --- Top products ---
    story.append(Paragraph("Top 10 Products by Revenue", styles["Heading2"]))
    prod_data = [["Product", "Category", "Units Sold", "Revenue"]]
    for row in top:
        prod_data.append(
            [
                row["product_name"],
                row["category"],
                str(row["units_sold"]),
                f"${row['revenue']:,.2f}",
            ]
        )
    prod_table = Table(prod_data, colWidths=[2.2 * inch, 1.8 * inch, 1.2 * inch, 1.3 * inch])
    prod_table.setStyle(_table_style())
    story.append(prod_table)

    doc.build(story)
    return output_path


def _table_style() -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a5568")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]
    )
