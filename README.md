# 개발 노트

C/C++, 그래픽스, Unreal Engine을 공부하며 쌓은 기술 노트를 주제별로 정리한 블로그입니다.

- content/articles 디렉터리에 글의 Markdown 파일이 있습니다.
- content/catalog.json에서 글 제목과 메뉴 순서를 관리합니다.
- content/media에 글의 이미지와 첨부 파일이 있습니다.
- docs에 정적 웹사이트를 빌드합니다. GitHub Pages의 게시 소스는 main 브랜치의 docs 디렉터리입니다.

Python에서 requirements.txt의 의존성을 설치한 다음 아래 명령으로 사이트를 다시 빌드합니다.

    python -m pip install -r requirements.txt
    python build.py content assets docs
