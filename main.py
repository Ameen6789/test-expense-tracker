
# from fastmcp import FastMCP
# import aiosqlite3
# import os
# from contextlib import closing
# import tempfile
# import asyncio
# TEMP_DIR=tempfile.gettempdir()

# mcp = FastMCP(name="expense tracker")

# DB_PATH = os.path.join(
#     TEMP_DIR,
#     "expense.db"
# )


# async def get_connection():
#     conn = aiosqlite3.connect(DB_PATH)
#     conn.row_factory = aiosqlite3.Row
#     return conn


# async def init_db():
#     with closing(get_connection()) as conn:
#         conn.execute("""
#             CREATE TABLE IF NOT EXISTS expenses (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 category TEXT NOT NULL,
#                 sub_category TEXT,
#                 amount REAL NOT NULL,
#                 note TEXT,
#                 date_created TIMESTAMP
#             )
#         """)

#         conn.commit()


# @mcp.tool
# async def add_expense(
#     category: str,
#     sub_category: str,
#     amount: float,
#     note: str,
#     date_created:str
# ):
#     """Add a new expense to the expense tracker."""
#     try:
#         with closing(get_connection()) as conn:
#             cursor = conn.execute("""
#                 INSERT INTO expenses
#                     (category, sub_category, amount,date_created, note)
#                 VALUES (?, ?, ?, ?,?)
#             """, (category, sub_category, amount,date_created, note))

#             conn.commit()

#             return {
#                 "message": "New expense added successfully",
#                 "id": cursor.lastrowid,
#                 "category": category,
#                 "sub_category": sub_category,
#                 "amount": amount,
#                 "date_created":date_created,
#                 "note": note
#             }

#     except aiosqlite3.Error as e:
#         return {"error": str(e)}


# @mcp.tool
# async def list_expense():
#     """List all expenses."""
#     try:
#         with closing(get_connection()) as conn:
#             rows = conn.execute(
#                 "SELECT * FROM expenses ORDER BY id DESC"
#             ).fetchall()

#             return [dict(row) for row in rows]

#     except aiosqlite3.Error as e:
#         return {"error": str(e)}
    

# # @mcp.tool
# # def list_expense():
# #     """List all expenses."""
# #     try:
# #         with closing(get_connection()) as conn:
# #             rows = conn.execute(
# #                 "SELECT * FROM expenses ORDER BY id DESC"
# #             ).fetchall()

# #             return [dict(row) for row in rows]

# #     except aiosqlite3.Error as e:
# #         return {"error": str(e)}


# if __name__ == "__main__":
#     init_db()
#     # mcp.run()
#     mcp.run(transport='http',host='0.0.0.0',port=8000)





# from fastmcp import FastMCP
# import aiosqlite
# import os
# import tempfile
# import asyncio

# TEMP_DIR = tempfile.gettempdir()
# DB_PATH = os.path.join(TEMP_DIR, "expense.db")

# mcp = FastMCP(name="expense tracker")


# async def init_db():
#     async with aiosqlite.connect(DB_PATH) as conn:
#         await conn.execute("""
#             CREATE TABLE IF NOT EXISTS expenses (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 category TEXT NOT NULL,
#                 sub_category TEXT,
#                 amount REAL NOT NULL,
#                 note TEXT,
#                 date_created TIMESTAMP
#             )
#         """)
#         await conn.commit()


# @mcp.tool
# async def add_expense(
#     category: str,
#     sub_category: str,
#     amount: float,
#     note: str,
#     date_created: str
# ):
#     """Add a new expense to the expense tracker."""
#     try:
#         async with aiosqlite.connect(DB_PATH) as conn:
#             conn.row_factory = aiosqlite.Row

#             cursor = await conn.execute("""
#                 INSERT INTO expenses
#                     (category, sub_category, amount, date_created, note)
#                 VALUES (?, ?, ?, ?, ?)
#             """, (category, sub_category, amount, date_created, note))

#             await conn.commit()

#             expense_id = cursor.lastrowid
#             await cursor.close()

#             return {
#                 "message": "New expense added successfully",
#                 "id": expense_id,
#                 "category": category,
#                 "sub_category": sub_category,
#                 "amount": amount,
#                 "date_created": date_created,
#                 "note": note
#             }

#     except aiosqlite.Error as e:
#         return {"error": str(e)}


# @mcp.tool
# async def list_expense():
#     """List all expenses."""
#     try:
#         async with aiosqlite.connect(DB_PATH) as conn:
#             conn.row_factory = aiosqlite.Row

#             cursor = await conn.execute("""
#                 SELECT * FROM expenses
#                 ORDER BY id DESC
#             """)

#             rows = await cursor.fetchall()
#             await cursor.close()

#             return [dict(row) for row in rows]

#     except aiosqlite.Error as e:
#         return {"error": str(e)}


# if __name__ == "__main__":
#     asyncio.run(init_db())
#     mcp.run(transport="http", host="0.0.0.0", port=8000)


from fastmcp import FastMCP
import os
import aiosqlite  # Changed: sqlite3 → aiosqlite
import tempfile
# Use temporary directory which should be writable
TEMP_DIR = tempfile.gettempdir()
DB_PATH = os.path.join(TEMP_DIR, "expenses.db")
# CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

print(f"Database path: {DB_PATH}")

mcp = FastMCP("ExpenseTracker")

def init_db():  # Keep as sync for initialization
    try:
        # Use synchronous sqlite3 just for initialization
        import sqlite3
        with sqlite3.connect(DB_PATH) as c:
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("""
                CREATE TABLE IF NOT EXISTS expenses(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    note TEXT DEFAULT ''
                )
            """)
            # Test write access
            c.execute("INSERT OR IGNORE INTO expenses(date, amount, category) VALUES ('2000-01-01', 0, 'test')")
            c.execute("DELETE FROM expenses WHERE category = 'test'")
            print("Database initialized successfully with write access")
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise

# Initialize database synchronously at module load
init_db()

@mcp.tool()
async def add_expense(date, amount, category, subcategory="", note=""):  # Changed: added async
    '''Add a new expense entry to the database.'''
    try:
        async with aiosqlite.connect(DB_PATH) as c:  # Changed: added async
            cur = await c.execute(  # Changed: added await
                "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
                (date, amount, category, subcategory, note)
            )
            expense_id = cur.lastrowid
            await c.commit()  # Changed: added await
            return {"status": "success", "id": expense_id, "message": "Expense added successfully"}
    except Exception as e:  # Changed: simplified exception handling
        if "readonly" in str(e).lower():
            return {"status": "error", "message": "Database is in read-only mode. Check file permissions."}
        return {"status": "error", "message": f"Database error: {str(e)}"}
    
@mcp.tool()
async def list_expenses(start_date, end_date):  # Changed: added async
    '''List expense entries within an inclusive date range.'''
    try:
        async with aiosqlite.connect(DB_PATH) as c:  # Changed: added async
            cur = await c.execute(  # Changed: added await
                """
                SELECT id, date, amount, category, subcategory, note
                FROM expenses
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC, id DESC
                """,
                (start_date, end_date)
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in await cur.fetchall()]  # Changed: added await
    except Exception as e:
        return {"status": "error", "message": f"Error listing expenses: {str(e)}"}

@mcp.tool()
async def summarize(start_date, end_date, category=None):  # Changed: added async
    '''Summarize expenses by category within an inclusive date range.'''
    try:
        async with aiosqlite.connect(DB_PATH) as c:  # Changed: added async
            query = """
                SELECT category, SUM(amount) AS total_amount, COUNT(*) as count
                FROM expenses
                WHERE date BETWEEN ? AND ?
            """
            params = [start_date, end_date]

            if category:
                query += " AND category = ?"
                params.append(category)

            query += " GROUP BY category ORDER BY total_amount DESC"

            cur = await c.execute(query, params)  # Changed: added await
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in await cur.fetchall()]  # Changed: added await
    except Exception as e:
        return {"status": "error", "message": f"Error summarizing expenses: {str(e)}"}

# @mcp.resource("expense:///categories", mime_type="application/json")  # Changed: expense:// → expense:///
# def categories():
#     try:
#         # Provide default categories if file doesn't exist
#         default_categories = {
#             "categories": [
#                 "Food & Dining",
#                 "Transportation",
#                 "Shopping",
#                 "Entertainment",
#                 "Bills & Utilities",
#                 "Healthcare",
#                 "Travel",
#                 "Education",
#                 "Business",
#                 "Other"
#             ]
#         }
        
#         try:
#             with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
#                 return f.read()
#         except FileNotFoundError:
#             import json
#             return json.dumps(default_categories, indent=2)
#     except Exception as e:
#         return f'{{"error": "Could not load categories: {str(e)}"}}'

# Start the server
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
    # mcp.run()