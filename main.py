
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



from fastmcp import FastMCP
import aiosqlite
import os
import tempfile
import asyncio

TEMP_DIR = tempfile.gettempdir()
DB_PATH = os.path.join(TEMP_DIR, "expense.db")

mcp = FastMCP(name="expense tracker")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                sub_category TEXT,
                amount REAL NOT NULL,
                note TEXT,
                date_created TIMESTAMP
            )
        """)
        await conn.commit()


@mcp.tool
async def add_expense(
    category: str,
    sub_category: str,
    amount: float,
    note: str,
    date_created: str
):
    """Add a new expense to the expense tracker."""
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row

            cursor = await conn.execute("""
                INSERT INTO expenses
                    (category, sub_category, amount, date_created, note)
                VALUES (?, ?, ?, ?, ?)
            """, (category, sub_category, amount, date_created, note))

            await conn.commit()

            expense_id = cursor.lastrowid
            await cursor.close()

            return {
                "message": "New expense added successfully",
                "id": expense_id,
                "category": category,
                "sub_category": sub_category,
                "amount": amount,
                "date_created": date_created,
                "note": note
            }

    except aiosqlite.Error as e:
        return {"error": str(e)}


@mcp.tool
async def list_expense():
    """List all expenses."""
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row

            cursor = await conn.execute("""
                SELECT * FROM expenses
                ORDER BY id DESC
            """)

            rows = await cursor.fetchall()
            await cursor.close()

            return [dict(row) for row in rows]

    except aiosqlite.Error as e:
        return {"error": str(e)}


if __name__ == "__main__":
    asyncio.run(init_db())
    mcp.run(transport="http", host="0.0.0.0", port=8000)
