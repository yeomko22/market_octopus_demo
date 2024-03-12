from datetime import datetime
from typing import List, Optional


def generate_news_based_answer_prompt(
    instruct: str,
    question: str,
    news: List[dict],
    ticker: Optional[str] = None,
    ticker_name: Optional[str] = None,
) -> str:
    news_text = ""
    for i, content in enumerate(news):
        news_text += f"""
title: {content["title"]}  
url: {content["url"]}  
related_paragraph: {content["relatedParagraph"]}  
"""
    prompt = f"""
{instruct}
--- 
today: {datetime.now().strftime("%Y-%m-%d")}  
question: {question}  
"""
    if ticker:
        prompt += f"selected ticker: {ticker} ({ticker_name})\n"
    if news:
        prompt += f"\nrelated news\n{news_text}"
    prompt += "---"
    return prompt.strip()
