
from fastmcp import FastMCP
import sqlite3
import os
from contextlib import closing

mcp = FastMCP(name="expense tracker")

db_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "expense.db"
)


def get_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_connection()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                sub_category TEXT,
                amount REAL NOT NULL,
                note TEXT,
                date_created TIMESTAMP
            )
        """)

        conn.commit()


@mcp.tool
def add_expense(
    category: str,
    sub_category: str,
    amount: float,
    note: str,
    date_created:str
):
    """Add a new expense to the expense tracker."""
    try:
        with closing(get_connection()) as conn:
            cursor = conn.execute("""
                INSERT INTO expenses
                    (category, sub_category, amount,date_created, note)
                VALUES (?, ?, ?, ?,?)
            """, (category, sub_category, amount,date_created, note))

            conn.commit()

            return {
                "message": "New expense added successfully",
                "id": cursor.lastrowid,
                "category": category,
                "sub_category": sub_category,
                "amount": amount,
                "date_created":date_created,
                "note": note
            }

    except sqlite3.Error as e:
        return {"error": str(e)}


@mcp.tool
def list_expense():
    """List all expenses."""
    try:
        with closing(get_connection()) as conn:
            rows = conn.execute(
                "SELECT * FROM expenses ORDER BY id DESC"
            ).fetchall()

            return [dict(row) for row in rows]

    except sqlite3.Error as e:
        return {"error": str(e)}
    

# @mcp.tool
# def list_expense():
#     """List all expenses."""
#     try:
#         with closing(get_connection()) as conn:
#             rows = conn.execute(
#                 "SELECT * FROM expenses ORDER BY id DESC"
#             ).fetchall()

#             return [dict(row) for row in rows]

#     except sqlite3.Error as e:
#         return {"error": str(e)}


if __name__ == "__main__":
    init_db()
    # mcp.run()
    mcp.run(transport='http',host='0.0.0.0',port=8000)
