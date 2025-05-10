import sqlite3
import re


def execute_sql(db_path, query, params=()):
    """SQLite에 SQL 실행 함수"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()


def update_image_links(
    content: str, raw_blog_url: str, blog_path: str, folder_path: str
) -> str:
    """
    GitHub 이미지 경로를 Discourse에서 사용할 수 있도록 업데이트
    """
    pattern = r"!\[([^\]]*)\]\(([^)]+)\)"

    def replace_image_link(match):
        alt_text = match.group(1)
        img_path = match.group(2)

        image_url = f"{raw_blog_url}{blog_path}/{folder_path}/{img_path}"
        return f"![{alt_text}]({image_url})"

    updated_content = re.sub(pattern, replace_image_link, content)
    return updated_content
