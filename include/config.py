import os
from dotenv import load_dotenv

load_dotenv()

SQLITE_DB_PATH = "/tmp/latest_blog.db"
SQLITE_TABLE_NAME = "latest_blog"
TRANSLATED_BLOG_DIR = "/tmp/translated_blog"
REPO_URL = "https://github.com/apache/airflow-site.git"
RAW_BLOG_DIR = "https://raw.githubusercontent.com/apache/airflow-site/refs/heads/main/"
BLOG_PATH = "landing-pages/site/content/en/blog"
LOCAL_REPO_DIR = "/tmp/airflow_blog_repo"
DISCOURSE_TOPIC_CATEGORY = 3
DISCOURSE_URL = "https://discourse.airflow-kr.org"


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCOURSE_API_KEY = os.getenv("DISCOURSE_API_KEY")
DISCOURSE_USERNAME = os.getenv("DISCOURSE_USERNAME")

SYSTEM_PROMPT = (
    "당신은 숙련된 한국어 번역가이며 Apache Airflow에 대한 기술 블로그 번역에 능숙합니다. "
    "블로그 원문은 영어로 되어 있으며, 대상 독자는 한국의 개발자 커뮤니티입니다. "
    "내용의 정확성을 유지하면서 자연스럽고 전문적인 한국어로 번역하세요. "
    "마크다운 형식과 코드 블록은 그대로 유지하되, 제목과 문장 구성은 한국어 독자에게 어울리도록 조정하세요. "
    "코드 블록(```)과 제목(#, ## 등), 링크([text](url)) 형식을 절대 변경하지 마세요."
    "내용을 절대 축약하거나 삭제하지 마세요."
)

DISCLAIMER = (
    "\n\n---\n\n"
    "본 글은 Apache Airflow 블로그 글을 GPT 모델을 활용하여 번역한 내용입니다. 따라서 원문의 내용 또는 의도와 다르게 정리된 내용이 있을 수 있습니다.\n"
    "관심있는 내용이시라면 원문도 함께 참고해주세요! [https://airflow.apache.org/blog/](https://airflow.apache.org/blog/)\n"
    "읽으시면서 어색하거나 잘못된 내용을 발견하시면 댓글로 알려주시면 감사드리겠습니다."
)
