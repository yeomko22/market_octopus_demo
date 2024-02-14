import streamlit as st
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(st.secrets["DATABASE_URL"], echo=False, pool_pre_ping=True)
Sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def insert_question_answer(question: str, answer: dict):
    write_sql = text("INSERT INTO question_answer (question, answer) VALUES (:question, :answer)")
    answer_str = json.dumps(answer, default=str, ensure_ascii=False)
    with Sessionmaker() as session:
        session.execute(write_sql, {"question": question, "answer": answer_str})
        session.commit()


def select_total_questions() -> int:
    with Sessionmaker() as session:
        select_sql = text("SELECT COUNT(*) FROM question_answer")
        result = session.execute(select_sql)
    result = result.scalar()
    return result


def select_questions(page: int, page_size: int = 10):
    select_sql = text(f"""
SELECT
    id,
    question,
    created_at
FROM
    question_answer
ORDER BY id DESC
LIMIT {page_size}
OFFSET {page_size * (page - 1)}
""")
    with Sessionmaker() as session:
        result = session.execute(select_sql)
    result = result.fetchall()
    return result


def select_question_answer(question_id: int):
    select_sql = text(f"""
SELECT
    created_at,
    question,
    answer
FROM
    question_answer
WHERE
    id={question_id}
""")
    with Sessionmaker() as session:
        result = session.execute(select_sql)
    result = result.fetchone()
    return result
