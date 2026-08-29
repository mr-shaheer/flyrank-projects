"""
db.py
-----
SQLite setup + seed data for the reporting pipeline.

Schema:
    customers(id, name, region)
    products(id, name, category, unit_price)
    orders(id, customer_id, order_date)
    order_items(id, order_id, product_id, quantity)

In a real project this would be Postgres/MySQL; SQLite is used here so the
whole thing runs with zero external services. The aggregation queries are
written in plain SQL (not pulled row-by-row into Python) on purpose --
that's the point of the exercise.
"""

import sqlite3
import random
import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "reports.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(seed: bool = True) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript(
        """
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS report_jobs;

        CREATE TABLE customers (
            id      INTEGER PRIMARY KEY,
            name    TEXT NOT NULL,
            region  TEXT NOT NULL
        );

        CREATE TABLE products (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            category    TEXT NOT NULL,
            unit_price  REAL NOT NULL
        );

        CREATE TABLE orders (
            id           INTEGER PRIMARY KEY,
            customer_id  INTEGER NOT NULL REFERENCES customers(id),
            order_date   TEXT NOT NULL
        );

        CREATE TABLE order_items (
            id          INTEGER PRIMARY KEY,
            order_id    INTEGER NOT NULL REFERENCES orders(id),
            product_id  INTEGER NOT NULL REFERENCES products(id),
            quantity    INTEGER NOT NULL
        );

        -- Background-job bookkeeping table.
        -- Note: no PDF bytes live in here, only a path/link (the whole
        -- point of "store and link, don't pass 20MB around").
        CREATE TABLE report_jobs (
            id           TEXT PRIMARY KEY,
            status       TEXT NOT NULL,       -- pending | running | done | failed
            report_type  TEXT NOT NULL,
            params       TEXT,                -- JSON string of query params
            file_path    TEXT,                -- link/reference to the artifact
            error        TEXT,
            created_at   TEXT NOT NULL,
            started_at   TEXT,
            finished_at  TEXT
        );
        """
    )

    if seed:
        regions = ["North", "South", "East", "West"]
        customers = [(i, f"Customer {i}", random.choice(regions)) for i in range(1, 31)]
        cur.executemany("INSERT INTO customers VALUES (?,?,?)", customers)

        categories = ["Electronics", "Home", "Sporting Goods", "Books", "Toys"]
        products = [
            (i, f"Product {i}", random.choice(categories), round(random.uniform(5, 250), 2))
            for i in range(1, 41)
        ]
        cur.executemany("INSERT INTO products VALUES (?,?,?,?)", products)

        start = datetime.date(2026, 1, 1)
        orders = []
        order_items = []
        order_id = 1
        item_id = 1
        for day_offset in range(240):  # ~8 months of activity
            order_date = start + datetime.timedelta(days=day_offset)
            for _ in range(random.randint(0, 6)):
                cust_id = random.randint(1, 30)
                orders.append((order_id, cust_id, order_date.isoformat()))
                for _ in range(random.randint(1, 4)):
                    prod_id = random.randint(1, 40)
                    qty = random.randint(1, 5)
                    order_items.append((item_id, order_id, prod_id, qty))
                    item_id += 1
                order_id += 1

        cur.executemany("INSERT INTO orders VALUES (?,?,?)", orders)
        cur.executemany("INSERT INTO order_items VALUES (?,?,?,?)", order_items)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
