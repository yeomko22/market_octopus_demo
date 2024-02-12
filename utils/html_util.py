html_template = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
    <meta charset="UTF-8">
    <title>분할 화면 예제</title>
    <style>
        /* 컨테이너 스타일 설정 */
        .container {{
            display: flex; /* Flexbox 레이아웃 사용 */
        }}

        /* iframe과 텍스트 영역을 동일한 크기로 설정 */
        .iframe-container {{
            flex: 7; /* flex 항목이 차지할 수 있는 공간의 비율 설정 */
            padding: 10px; /* 안쪽 여백 설정 */
        }}
        /* iframe과 텍스트 영역을 동일한 크기로 설정 */
        .text-container {{
            flex: 3; /* flex 항목이 차지할 수 있는 공간의 비율 설정 */
            padding: 10px; /* 안쪽 여백 설정 */
        }}

        /* iframe 스타일 설정 */
        iframe {{
            width: 100%; /* 부모 요소의 전체 너비 차지 */
            height: 100vh; /* 높이 설정 */
            border: none; /* 테두리 제거 */
        }}
    </style>
    </head>
    <body>

    <div class="container">
        <!-- iframe 컨테이너 -->
        <div class="iframe-container">
            <iframe 
                src="{origin_url}" 
                title="외부 콘텐츠"
            ></iframe>
        </div>

        <!-- 텍스트 컨테이너 -->
        <div class="text-container">
            <h1>원문</h1>
            <a href="{reference_url}">{reference_url}</a>
            <h1>관련 문단</h1>
            <p>{related_paragraph}</p>
        </div>
    </div>

    </body>
    </html>
    """


def get_reference_page_html(origin_url: str, reference_url: str, related_paragraph: str) -> str:
    return html_template.format(
        origin_url=origin_url,
        reference_url=reference_url,
        related_paragraph=related_paragraph
    )
