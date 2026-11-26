---
title: "Rule of Three, Five, Zero"
category: content/categories/topic-01-03.json
order: 120
---
뭔지 모르겠지만.. 알아보자\~

---

<b>Rule of Three</b>

소멸자, 복사 생성자, 복사 대입 연산자 중 하나를 직접 선언해야 하는 클래스라면 나머지 두 연산도 함께 검토한다.

<b>Rule of Five</b>

이동 생성자와 이동 대입 연산자까지 포함한 다섯 특수 멤버 함수의 동작을 함께 검토한다. 타입에 맞게 직접 구현하거나 기본 동작을 사용하고, 지원하지 않는 연산은 삭제할 수 있다.

<b>Rule of Zero</b>

소멸자, 이동 생성자, 복사 생성자, 이동 대입 연산자, 복사 대입 연산자 다섯 가지 특수 멤버 함수들을 필요로 하지 않도록 디자인 하는 것이다.

기본적인 방법으로는 구식 스타일의 메모리 할당을 피하는 것이다.

A클래스를 2차원 배열로 동적할당 하기 위해 A\*\*으로 선언하지 말고 vector\<vector\<A>> 이런식으로 사용하자. vector는 메모리 할당을 알아서 해주기 때문에 위에 상기된 5가지 멤버함수을 사용할 일이 없다.

[C++ Core Guidelines C.20·C.21](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#Rc-five)
