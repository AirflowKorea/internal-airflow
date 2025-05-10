from airflow.decorators import dag, task
from airflow.datasets import Dataset
from datetime import datetime, timedelta
import os
import requests
import logging
import sqlite3
import frontmatter
from typing import Optional, Dict, Any
from openai import OpenAI
from include.utils import update_image_links
from include.config import (
    SQLITE_DB_PATH,
    SQLITE_TABLE_NAME,
    OPENAI_API_KEY,
    TRANSLATED_BLOG_DIR,
    BLOG_PATH,
    RAW_BLOG_DIR,
    DISCOURSE_API_KEY,
    DISCOURSE_TOPIC_CATEGORY,
    DISCOURSE_URL,
    DISCOURSE_USERNAME,
    SYSTEM_PROMPT,
    DISCLAIMER,
)

t_log = logging.getLogger("airflow.task")

default_args = {
    "owner": "airflow-kr",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

@dag(
    schedule=[Dataset(SQLITE_DB_PATH)],
    start_date=datetime(2025, 5, 10),
    catchup=False,
    default_args=default_args,
    max_active_runs=1,
    tags=["AirflowBlog", "Translate", "ChatGPT"],
)
def translate_and_post():
    @task
    def fetch_latest_post() -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT folder, content, date
            FROM {SQLITE_TABLE_NAME}
            ORDER BY date DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()

        if row:
            return {"folder": row[0], "content": row[1], "date": row[2]}
        return None

    @task
    def translate_post(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        if not data:
            t_log.info("No data to translate.")
            return None

        if not OPENAI_API_KEY:
            t_log.error("OpenAI API Key is not set.")
            return None

        system_prompt = SYSTEM_PROMPT

        updated_content = update_image_links(
            data["content"], RAW_BLOG_DIR, BLOG_PATH, data["folder"]
        )

        prompt = f"다음의 마크다운 블로그 글을 자연스러운 한국어로 번역해줘:\n\n{updated_content}"

        client = OpenAI(api_key=OPENAI_API_KEY)

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )
            translated_content = response.choices[0].message.content
        except Exception as e:
            t_log.error(f"Error calling OpenAI API: {e}")
            return None

        return {"folder": data["folder"], "translated": translated_content}

    @task
    def save_translated_post(data: Optional[Dict[str, str]]) -> Optional[str]:
        if not data:
            return None

        os.makedirs(TRANSLATED_BLOG_DIR, exist_ok=True)
        file_name = f"{data['folder']}_index.ko.md"
        file_path = os.path.join(TRANSLATED_BLOG_DIR, file_name)

        with open(file_path, "w") as f:
            f.write(data["translated"])

        return file_path

    @task
    def post_to_discourse(file_path: Optional[str]):
        if not file_path or not os.path.exists(file_path):
            t_log.warning("Translated blog file not found.")
            return

        try:
            post = frontmatter.load(file_path)
            title = post.get("title")
            body = post.content
            body += DISCLAIMER
        except Exception as e:
            t_log.error(f"Error parsing frontmatter: {e}")
            return

        headers = {
            "Content-Type": "application/json",
            "Api-Key": DISCOURSE_API_KEY,
            "Api-Username": DISCOURSE_USERNAME,
        }

        payload = {
            "title": title,
            "raw": body,
            "category": DISCOURSE_TOPIC_CATEGORY,
        }

        response = requests.post(
            f"{DISCOURSE_URL}/posts.json", headers=headers, json=payload
        )

        if response.status_code in [200, 201]:
            t_log.info(f"Successfully posted to Discourse: {title}")
        else:
            t_log.error(
                f"Failed to post to Discourse: {response.status_code}, {response.text}"
            )

    post = fetch_latest_post()
    translated = translate_post(post)
    file_path = save_translated_post(translated)
    post_to_discourse(file_path)


translate_and_post()
