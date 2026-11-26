# 개발 노트

C/C++, 그래픽스, Unreal Engine을 공부하며 쌓은 기술 노트를 주제별로 정리한 블로그입니다.

## 블로그 편집

[Pages CMS](https://app.pagescms.org/)에 GitHub 계정으로 로그인하고 `Durumyisking/durumyisking.github.io`의 `main`을 엽니다.

- **게시글**에서 새 글을 만들거나 제목, 본문, 이미지, 코드 블록을 수정합니다. 카테고리를 바꾸면 글이 해당 목차로 이동합니다.
- **카테고리**에서 이름, 상위 카테고리, 순서를 바꿀 수 있습니다. 같은 위치에서는 작은 순서 번호가 먼저 표시됩니다.
- 게시글의 삭제 메뉴를 쓰면 배포 후 목차와 공개 페이지에서 글이 사라집니다. 이전 버전은 GitHub 변경 이력에서 찾아볼 수 있습니다.
- 접기나 영상처럼 기존 HTML을 포함한 글을 편집할 때는 **Source** 모드에서 해당 부분을 수정할 수 있습니다.

저장과 삭제는 GitHub에 기록되고 [Actions](https://github.com/Durumyisking/durumyisking.github.io/actions)에서 사이트를 다시 빌드해 게시합니다.

## 로컬 빌드

```sh
python -m pip install -r requirements.txt
python -m unittest discover -v
python build.py content assets _site
```
