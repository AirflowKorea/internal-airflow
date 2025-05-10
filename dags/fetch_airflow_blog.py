from airflow.decorators import dag, task
from datetime import datetime, timedelta
import os
import subprocess
import re
import sqlite3
from include.utils import execute_sql
from include.config import (
    REPO_URL,
    BLOG_PATH,
    LOCAL_REPO_DIR,
    SQLITE_DB_PATH,
    SQLITE_TABLE_NAME,
)

default_args = {
    "owner": "airflow-kr",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    schedule="@daily",
    start_date=datetime(2025, 5, 10),
    catchup=False,
    default_args=default_args,
    tags=["github", "blog", "airflow-site"],
)
def fetch_latest_airflow_blog():
    @task
    def create_blog_table():
        sql = f"""
            CREATE TABLE IF NOT EXISTS {SQLITE_TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder TEXT UNIQUE,
                content TEXT,
                date TEXT
            )
        """
        execute_sql(SQLITE_DB_PATH, sql)

    @task
    def clone_repo() -> str:
        if os.path.exists(LOCAL_REPO_DIR):
            subprocess.run(["rm", "-rf", LOCAL_REPO_DIR])
        subprocess.run(
            ["git", "clone", "--depth", "1", REPO_URL, LOCAL_REPO_DIR], check=True
        )
        return os.path.join(LOCAL_REPO_DIR, BLOG_PATH)

    @task
    def detect_latest_post(blog_dir: str) -> dict | None:
        latest_post = None
        latest_date = datetime.min

        for folder in os.listdir(blog_dir):
            index_path = os.path.join(blog_dir, folder, "index.md")
            if not os.path.isfile(index_path):
                continue

            with open(index_path, "r") as f:
                content = f.read()

            match = re.search(r'date:\s*"?(?P<date>[\d-]+)"?', content)
            if match:
                post_date = datetime.strptime(match.group("date"), "%Y-%m-%d")
                if post_date > latest_date:
                    latest_date = post_date
                    latest_post = {
                        "folder": folder,
                        "content": content,
                        "date": post_date.strftime("%Y-%m-%d"),
                    }
        return latest_post

    @task
    @task
    def save_to_sqlite(data: dict | None):
        if not data:
            return

        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()

        cursor.execute(f"SELECT MAX(date) FROM {SQLITE_TABLE_NAME}")
        result = cursor.fetchone()
        latest_saved_date = result[0] if result and result[0] else None

        if latest_saved_date is None or data["date"] > latest_saved_date:
            cursor.execute(
                f"""
                INSERT INTO {SQLITE_TABLE_NAME} (folder, content, date)
                VALUES (?, ?, ?)
            """,
                (data["folder"], data["content"], data["date"]),
            )

        conn.commit()
        conn.close()

    create_blog_table()
    repo_path = clone_repo()
    latest_post = detect_latest_post(repo_path)
    save_to_sqlite(latest_post)


fetch_latest_airflow_blog()
