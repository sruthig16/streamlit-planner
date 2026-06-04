import sqlite3

conn = sqlite3.connect("planner.db")
cursor = conn.cursor()

tables = ["plans", "buckets", "tasks", "checklist_items"]

for table in tables:
    print("\n" + "=" * 50)
    print(f"TABLE: {table}")
    print("=" * 50)

    rows = cursor.execute(f"SELECT * FROM {table}").fetchall()

    if rows:
        for row in rows:
            print(row)
    else:
        print("No records found.")

conn.close()