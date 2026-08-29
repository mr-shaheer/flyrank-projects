"""
queries.py
----------
All aggregation happens in SQL. The Python layer just shapes the params
and hands back rows -- no manual summing/grouping in application code.
"""

from app.db import get_connection


def sales_summary_by_region(start_date: str, end_date: str):
    """Total revenue and order count per region, for a date range."""
    sql = """
        SELECT
            c.region                                   AS region,
            COUNT(DISTINCT o.id)                        AS order_count,
            SUM(oi.quantity * p.unit_price)              AS revenue
        FROM orders o
        JOIN customers c    ON c.id = o.customer_id
        JOIN order_items oi ON oi.order_id = o.id
        JOIN products p     ON p.id = oi.product_id
        WHERE o.order_date BETWEEN ? AND ?
        GROUP BY c.region
        ORDER BY revenue DESC
    """
    with get_connection() as conn:
        return conn.execute(sql, (start_date, end_date)).fetchall()


def top_products(start_date: str, end_date: str, limit: int = 10):
    """Best-selling products by revenue, for a date range."""
    sql = """
        SELECT
            p.name                          AS product_name,
            p.category                      AS category,
            SUM(oi.quantity)                 AS units_sold,
            SUM(oi.quantity * p.unit_price)   AS revenue
        FROM order_items oi
        JOIN products p ON p.id = oi.product_id
        JOIN orders o   ON o.id = oi.order_id
        WHERE o.order_date BETWEEN ? AND ?
        GROUP BY p.id
        ORDER BY revenue DESC
        LIMIT ?
    """
    with get_connection() as conn:
        return conn.execute(sql, (start_date, end_date, limit)).fetchall()


def daily_revenue(start_date: str, end_date: str):
    """Revenue per day, for a trend line/table in the report."""
    sql = """
        SELECT
            o.order_date                     AS order_date,
            SUM(oi.quantity * p.unit_price)   AS revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        JOIN products p     ON p.id = oi.product_id
        WHERE o.order_date BETWEEN ? AND ?
        GROUP BY o.order_date
        ORDER BY o.order_date
    """
    with get_connection() as conn:
        return conn.execute(sql, (start_date, end_date)).fetchall()


def overall_totals(start_date: str, end_date: str):
    """Single-row headline numbers for the report cover section."""
    sql = """
        SELECT
            COUNT(DISTINCT o.id)              AS total_orders,
            COUNT(DISTINCT o.customer_id)     AS unique_customers,
            SUM(oi.quantity * p.unit_price)    AS total_revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        JOIN products p     ON p.id = oi.product_id
        WHERE o.order_date BETWEEN ? AND ?
    """
    with get_connection() as conn:
        return conn.execute(sql, (start_date, end_date)).fetchone()
