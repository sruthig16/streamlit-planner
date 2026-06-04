import sqlite3
from pathlib import Path

DB_PATH = Path("planner.db")

DEFAULT_BUCKETS = [
    "Backlog",
    "Up next",
    "In progress",
    "Blocked",
    "Completed",
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buckets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            position INTEGER NOT NULL,
            FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL,
            bucket_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            priority TEXT DEFAULT 'Medium',
            assignee TEXT,
            labels TEXT,
            completed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE,
            FOREIGN KEY (bucket_id) REFERENCES buckets(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checklist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def create_plan(name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO plans (name) VALUES (?)", (name,))
    plan_id = cursor.lastrowid

    for position, bucket_name in enumerate(DEFAULT_BUCKETS):
        cursor.execute(
            "INSERT INTO buckets (plan_id, name, position) VALUES (?, ?, ?)",
            (plan_id, bucket_name, position)
        )

    conn.commit()
    conn.close()
    return plan_id


def get_plans():
    conn = get_connection()
    plans = conn.execute(
        "SELECT * FROM plans ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return plans


def get_plan(plan_id):
    conn = get_connection()
    plan = conn.execute(
        "SELECT * FROM plans WHERE id = ?",
        (plan_id,)
    ).fetchone()
    conn.close()
    return plan


def get_buckets(plan_id):
    conn = get_connection()
    buckets = conn.execute(
        "SELECT * FROM buckets WHERE plan_id = ? ORDER BY position",
        (plan_id,)
    ).fetchall()
    conn.close()
    return buckets
def create_task(
    plan_id,
    bucket_id,
    title,
    description="",
    due_date=None,
    priority="Medium",
    assignee="",
    labels="",
):
    conn = get_connection()
    cursor = conn.cursor()

    due_date_text = str(due_date) if due_date else None

    cursor.execute(
        """
        INSERT INTO tasks (
            plan_id, bucket_id, title, description,
            due_date, priority, assignee, labels
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            plan_id,
            bucket_id,
            title,
            description,
            due_date_text,
            priority,
            assignee,
            labels,
        ),
    )

    conn.commit()
    conn.close()


def get_tasks(plan_id):
    conn = get_connection()
    tasks = conn.execute(
        """
        SELECT
            tasks.*,
            buckets.name AS bucket_name
        FROM tasks
        JOIN buckets ON tasks.bucket_id = buckets.id
        WHERE tasks.plan_id = ?
        ORDER BY tasks.created_at DESC
        """,
        (plan_id,),
    ).fetchall()
    conn.close()
    return tasks
def update_task_status(task_id, bucket_id, completed):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET bucket_id = ?, completed = ?
        WHERE id = ?
        """,
        (
            bucket_id,
            1 if completed else 0,
            task_id,
        ),
    )

    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,),
    )

    conn.commit()
    conn.close()
def add_checklist_item(task_id, text):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO checklist_items (task_id, text)
        VALUES (?, ?)
        """,
        (task_id, text),
    )

    conn.commit()
    conn.close()


def get_checklist_items(task_id):
    conn = get_connection()
    items = conn.execute(
        """
        SELECT *
        FROM checklist_items
        WHERE task_id = ?
        ORDER BY id
        """,
        (task_id,),
    ).fetchall()
    conn.close()
    return items


def update_checklist_item(item_id, completed):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE checklist_items
        SET completed = ?
        WHERE id = ?
        """,
        (1 if completed else 0, item_id),
    )

    conn.commit()
    conn.close()


def delete_checklist_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM checklist_items
        WHERE id = ?
        """,
        (item_id,),
    )

    conn.commit()
    conn.close()


def get_checklist_progress(task_id):
    conn = get_connection()

    total = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM checklist_items
        WHERE task_id = ?
        """,
        (task_id,),
    ).fetchone()["count"]

    completed = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM checklist_items
        WHERE task_id = ? AND completed = 1
        """,
        (task_id,),
    ).fetchone()["count"]

    conn.close()

    return completed, total
def update_task_details(
    task_id,
    title,
    description,
    due_date,
    priority,
    assignee,
    labels,
):
    conn = get_connection()
    cursor = conn.cursor()

    due_date_text = str(due_date) if due_date else None

    cursor.execute(
        """
        UPDATE tasks
        SET title = ?,
            description = ?,
            due_date = ?,
            priority = ?,
            assignee = ?,
            labels = ?
        WHERE id = ?
        """,
        (
            title,
            description,
            due_date_text,
            priority,
            assignee,
            labels,
            task_id,
        ),
    )

    conn.commit()
    conn.close()
def rename_plan(plan_id, new_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE plans
        SET name = ?
        WHERE id = ?
        """,
        (new_name, plan_id),
    )

    conn.commit()
    conn.close()


def delete_plan(plan_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM plans
        WHERE id = ?
        """,
        (plan_id,),
    )

    conn.commit()
    conn.close()