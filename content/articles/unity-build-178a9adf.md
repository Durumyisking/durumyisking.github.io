---
title: "Unity Build"
category: content/categories/topic-01-05.json
order: 40
---
- 원하는 파일들을 합쳐서 하나의 Obj파일을 만들어서 빌드하는것
- VS 2022 이전에는 직접 헤더들을 지정해줘서 빌드해야했지만
- VS 2022 부터는 옵션에서 설정 가능함

- 하지만 unity build를 무조건 사용을 안하는 이유는
- 하나의 obj에 모든 헤더를 넣기 때문에

```c++
// A
#include "all"
#include "A.h"

// B
// #include "all" 실수로 빼먹음
#include "B.h"
```

위 코드처럼 만들어진다.

unity build에서는 B가 A에서 선언한 all을 알고 있기때문에 해당 프로그램이 실행되겠지만

unity build를 끄면 B는 all을 모르기때문에 오류가 생길것이다.
