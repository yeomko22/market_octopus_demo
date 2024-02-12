import streamlit as st
import json
import pymysql


conn = pymysql.connect(
    host=st.secrets["mysql_host"],
    user=st.secrets["mysql_user"],
    password=st.secrets["mysql_password"],
    database=st.secrets["mysql_database"],
    port=st.secrets["mysql_port"],
)


def insert_question_answer(question: str, answer: dict):
    write_sql = "INSERT INTO question_answer (question, answer) VALUES (%s, %s)"
    answer_str = json.dumps(answer, default=str, ensure_ascii=False)
    with conn.cursor() as cursor:
        cursor.execute(write_sql, (question, answer_str))
        conn.commit()


def select_total_questions() -> int:
    select_sql = "SELECT COUNT(*) FROM question_answer"
    with conn.cursor() as cursor:
        cursor.execute(select_sql)
        result = cursor.fetchone()[0]
    return result


def select_questions(page: int, page_size: int = 10):
    select_sql = f"""
SELECT
    id,
    question, 
    created_at 
FROM
    question_answer
ORDER BY id DESC
LIMIT {page_size}
OFFSET {page_size * (page - 1)}
"""
    with conn.cursor() as cursor:
        cursor.execute(select_sql)
        result = cursor.fetchall()
    return result
