from services.service_openai import generate_next_questions


def test_generate_next_questions():
    question = "최근 발표된 미국 금리 인하가 주식 시장에 어떤 영향을 미칠까?"
    answer = """
미국 금리 인하 예상이 주식 시장에 미치는 영향을 묻는 질문입니다.

금리 인하 기대 하락, 주식 시장에 불확실성 증가

최근의 데이터들이 섞인 결과를 내놓으면서 금리 인하에 대한 기대가 줄고 있어 주식 시장에 새로운 불확실성이 생겼어요.
이미 주식 시장에서는 차익 실현이 일어날 수 있는 환경이며, Fed가 공격적인 금리 정책을 유지할 가능성이 있어요.
CME FedWatch Tool에 따르면, 3월의 금리 인하 가능성이 이달 초 확률 80%에서 50% 미만으로 격감했어요.
줄어든 인하 가능성은 주식과 채권 시장의 변동성 증가로 이어질 수 있으며, 투자자들은 더 보수적인 입장을 취할지도 몰라요.
Fed는 대개 중요한 정책 변경을 천명하기 전에 분명한 신호를 전달하는 경향이 있어, 현재 뚜렷한 신호가 없다는 점이 금리 인하에 대한 기대를 더 낮출 수 있어요.
    """.strip()
    questions = generate_next_questions(question, answer)
    assert isinstance(questions, list)
    assert len(questions) == 3
